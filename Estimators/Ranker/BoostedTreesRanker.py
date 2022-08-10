from typing import List

import numpy as np
import pandas as pd
from lightgbm import LGBMRanker

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.Ranker import Ranker
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class BoostedTreesRanker(Ranker):

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "metric": "ndcg",
        "n_estimators": 1000,
        "learning_rate": 0.01,
        "verbose": -1,
        "random_state": 0,
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

    def transform(self, samples: pd.DataFrame) -> pd.DataFrame:
        X = samples[self.feature_names].to_numpy()
        scores = self._ranker.predict(X)

        samples.loc[:, "score"] = scores

        samples.loc[:, "exp_score"] = np.exp(samples.loc[:, "score"])
        score_sums = samples.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        samples = samples.join(other=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")
        samples.loc[:, "win_probability"] = samples.loc[:, "exp_score"] / samples.loc[:, "sum_exp_scores"]

        return samples

    @property
    def ranker(self):
        return self._ranker
