from typing import List

import pandas as pd
import lightgbm

from Estimation.Ranker import Ranker
from SampleExtraction.Horse import Horse


class BoostedTreesRanker(Ranker):

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "metric": "ndcg",
        "device": "gpu",
        "n_estimators": 1000,
        "learning_rate": 0.01,
        "verbose": -1,
        "random_state": 0,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": 8,
    }

    def __init__(self, feature_subset: List[str], search_params: dict):
        super().__init__(feature_subset)
        if not search_params:
            search_params = {}

        self.feature_subset = feature_subset
        self._ranker = lightgbm.LGBMRanker()
        self.set_search_params(search_params)

    def fit(self, samples_train: pd.DataFrame):
        X = samples_train[self.feature_subset]
        y = samples_train[Horse.RELEVANCE_KEY]
        qid = samples_train.groupby(Horse.RACE_ID_KEY)[Horse.RACE_ID_KEY].count()

        self._ranker.fit(X=X, y=y, group=qid)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        X = samples_test[self.feature_subset]
        scores = self._ranker.predict(X)

        samples_test.loc[:, "score"] = scores

        return samples_test

    @property
    def ranker(self):
        return self._ranker

