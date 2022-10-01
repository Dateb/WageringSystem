from typing import List

import numpy as np
import pandas as pd
from lightgbm import LGBMRanker
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.Ranker import Ranker
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesRanker(Ranker):

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "metric": "ndcg",
        "n_estimators": 1000,
        "learning_rate": 0.01,
        "verbose": -1,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
    }

    def __init__(self, features: List[FeatureExtractor], search_params: dict):
        super().__init__(features, Horse.RELEVANCE_KEY)
        if not search_params:
            search_params = {}

        self.features = features
        self.feature_names = [feature.get_name() for feature in features]
        self._ranker = LGBMRanker()
        self.set_search_params(search_params)

    def fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        x_ranker = samples_train[self.feature_names].to_numpy()
        y_ranker = samples_train[self.label_name].to_numpy()
        qid = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        self._ranker.fit(X=x_ranker, y=y_ranker, group=qid)

    def transform(self, race_cards_sample: RaceCardsSample) -> RaceCardsSample:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names].to_numpy()
        scores = self._ranker.predict(X)

        return self.set_win_probabilities(race_cards_sample, scores)

    def transform_sequential(self, race_cards_sample: RaceCardsSample) -> RaceCardsSample:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names].to_numpy()
        y = race_cards_dataframe[self.label_name].to_numpy()
        qid = race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().values
        scores = np.zeros(shape=(len(X)))

        start_idx = 0
        for i in range(len(qid)):
            group_count = qid[i]
            x_group = X[start_idx:start_idx+group_count]
            y_group = y[start_idx:start_idx+group_count]

            scores[start_idx:start_idx+group_count] = self._ranker.predict(x_group)
            self._ranker.set_params(**{"n_estimators": 1})
            self._ranker.fit(X=x_group, y=y_group, group=[group_count], init_model=self._ranker.booster_)

            start_idx += group_count

        return self.set_win_probabilities(race_cards_sample, scores)

    def set_win_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceCardsSample:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return RaceCardsSample(race_cards_dataframe)

    @property
    def ranker(self):
        return self._ranker
