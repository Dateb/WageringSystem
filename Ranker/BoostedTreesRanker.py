from typing import List

import numpy as np
import pandas as pd
from lightgbm import LGBMRanker

from DataAbstraction.RaceCard import RaceCard
from Ranker.Ranker import Ranker
from DataAbstraction.Horse import Horse


def loglikelihood(y_true, y_pred):
    y_pred = 1. / (1. + np.exp(-y_pred))
    grad = y_pred - y_true
    hess = y_pred * (1. - y_pred)
    return grad, hess


class BoostedTreesRanker(Ranker):

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": loglikelihood,
        "metric": "ndcg",
        "n_estimators": 1000,
        "learning_rate": 0.01,
        "verbose": -1,
        "random_state": 0,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
    }

    def __init__(self, feature_subset: List[str], search_params: dict):
        super().__init__(feature_subset)
        if not search_params:
            search_params = {}

        self.feature_subset = feature_subset
        self._ranker = LGBMRanker()
        self.set_search_params(search_params)

    def fit(self, samples_train: pd.DataFrame):
        x_ranker = samples_train[self.feature_subset]
        print(x_ranker.shape)
        y_ranker = samples_train[Horse.RELEVANCE_KEY]
        qid = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        self._ranker.fit(
            X=x_ranker,
            y=y_ranker,
            group=qid,
        )

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        X = samples_test[self.feature_subset]
        scores = self._ranker.predict(X)

        print(scores)

        samples_test.loc[:, "score"] = scores

        samples_test.loc[:, "exp_score"] = np.exp(samples_test.loc[:, "score"])
        score_sums = samples_test.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        samples_test = samples_test.join(other=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")
        samples_test.loc[:, "win_probability"] = samples_test.loc[:, "exp_score"] / samples_test.loc[:, "sum_exp_scores"]

        return samples_test

    @property
    def ranker(self):
        return self._ranker

