from typing import List

import lightgbm
import numpy as np
import pandas as pd
from lightgbm import Dataset
from numpy import ndarray

from Betting.Bets.Bet import Bet
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.EstimationResult import EstimationResult
from Estimators.Ranker.Ranker import Ranker
from Estimators.place_calculation import compute_place_probabilities
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesRanker(Ranker):

    ranking_seed = 30

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "metric": "ndcg",
        "verbose": -1,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
        "device": "cpu",

        "seed": ranking_seed,
        "data_random_seed": ranking_seed,
        "feature_fraction_seed": ranking_seed,
        "objective_seed": ranking_seed,
        "bagging_seed": ranking_seed,
        "extra_seed": ranking_seed,
        "drop_seed": ranking_seed,
    }

    def __init__(self, features: List[FeatureExtractor], search_params: dict):
        super().__init__(features, Horse.RELEVANCE_KEY)
        if not search_params:
            search_params = {}

        self.features = features
        self.feature_names = [feature.get_name() for feature in features]

        self.categorical_feature_names = [feature.get_name() for feature in features if feature.is_categorical]

        self.set_parameter_set(search_params)
        self.booster = None

    def fit(self, samples_train: pd.DataFrame, num_boost_round: int):
        input_data = samples_train[self.feature_names]
        label = samples_train[self.label_name].astype(dtype="int")
        group = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        dataset = Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=self.categorical_feature_names,
        )

        self.booster = lightgbm.train(
            self.parameter_set,
            train_set=dataset,
            categorical_feature=self.categorical_feature_names,
            num_boost_round=num_boost_round,
        )

    def transform(self, race_cards_sample: RaceCardsSample) -> EstimationResult:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        scores = self.booster.predict(X)

        return self.set_probabilities(race_cards_sample, scores)

    def set_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> EstimationResult:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe)
        race_cards_dataframe["place_probability"] = "0"
        # race_cards_dataframe = self.set_place_probabilities(race_cards_dataframe)

        race_cards_dataframe["expected_value"] = race_cards_dataframe[Horse.WIN_PROBABILITY_KEY]\
                                                 * race_cards_dataframe[Horse.CURRENT_BETTING_ODDS_KEY]\
                                                 * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)

        return EstimationResult(race_cards_dataframe)

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return race_cards_dataframe

    def set_place_probabilities(self, race_cards_dataframe: pd.DataFrame) -> pd.DataFrame:
        grouped_win_information = race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[["win_probability", RaceCard.PLACE_NUM_KEY]].agg({
            "win_probability": lambda x: list(x),
            RaceCard.PLACE_NUM_KEY: "first"
        })

        win_information = [tuple(row) for row in grouped_win_information.values]
        place_probabilities = compute_place_probabilities(win_information)

        flattened_place_probabilities = [item for sublist in place_probabilities for item in sublist]

        race_cards_dataframe["place_probability"] = flattened_place_probabilities

        return race_cards_dataframe
