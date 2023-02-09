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
        race_cards_dataframe = self.set_place_probabilities(race_cards_dataframe)
        # race_cards_dataframe["place_probability"] = "0"

        race_cards_dataframe["expected_value"] = race_cards_dataframe["place_probability"]\
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
        race_cards_dataframe_prob_copy = race_cards_dataframe[[RaceCard.RACE_ID_KEY, Horse.NUMBER_KEY, "win_probability"]]
        race_cards_2_dataframe = pd.merge(
            left=race_cards_dataframe,
            right=race_cards_dataframe_prob_copy,
            how="outer",
            on=RaceCard.RACE_ID_KEY,
            suffixes=("", "_second"),
        )
        race_cards_2_dataframe = race_cards_2_dataframe[race_cards_2_dataframe[Horse.NUMBER_KEY] != race_cards_2_dataframe["number_second"]]
        race_cards_2_dataframe["place_2_probability"] = race_cards_2_dataframe["win_probability_second"] \
                                                      * race_cards_2_dataframe[Horse.WIN_PROBABILITY_KEY] / (1 - race_cards_2_dataframe["win_probability_second"])
        place_2_probabilities = race_cards_2_dataframe.groupby([RaceCard.RACE_ID_KEY, Horse.NUMBER_KEY]).agg(place_2_probability=("place_2_probability", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(
            right=place_2_probabilities,
            on=[RaceCard.RACE_ID_KEY, Horse.NUMBER_KEY],
            how="inner"
        )

        race_cards_3_dataframe = pd.merge(
            left=race_cards_2_dataframe,
            right=race_cards_dataframe_prob_copy,
            how="outer",
            on=RaceCard.RACE_ID_KEY,
            suffixes=("", "_third"),
        )

        race_cards_3_dataframe = race_cards_3_dataframe[race_cards_3_dataframe[Horse.NUMBER_KEY] != race_cards_3_dataframe["number_third"]]
        race_cards_3_dataframe = race_cards_3_dataframe[race_cards_3_dataframe["number_second"] != race_cards_3_dataframe["number_third"]]
        race_cards_3_dataframe["place_3_probability"] = race_cards_3_dataframe["win_probability_third"] * \
                                                        (race_cards_3_dataframe["win_probability_second"] / (1 - race_cards_3_dataframe["win_probability_third"])) * \
                                                        (race_cards_3_dataframe[Horse.WIN_PROBABILITY_KEY] / (1 - race_cards_3_dataframe["win_probability_third"] - race_cards_3_dataframe["win_probability_second"]))

        place_3_probabilities = race_cards_3_dataframe.groupby([RaceCard.RACE_ID_KEY, Horse.NUMBER_KEY]).agg(place_3_probability=("place_3_probability", "sum"))

        race_cards_dataframe = race_cards_dataframe.merge(
            right=place_3_probabilities,
            on=[RaceCard.RACE_ID_KEY, Horse.NUMBER_KEY],
            how="inner"
        )

        race_cards_dataframe["place_probability"] = race_cards_dataframe["win_probability"] \
                                                    + race_cards_dataframe["place_2_probability"] * (race_cards_dataframe[RaceCard.PLACE_NUM_KEY] >= 2) \
                                                    + race_cards_dataframe["place_3_probability"] * (race_cards_dataframe[RaceCard.PLACE_NUM_KEY] >= 3)

        return race_cards_dataframe
