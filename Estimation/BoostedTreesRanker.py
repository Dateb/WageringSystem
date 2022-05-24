from typing import List

import pandas as pd
import lightgbm

from SampleExtraction.Horse import Horse


class BoostedTreesRanker:

    def __init__(self, feature_names: List[str]):
        self.__feature_names = feature_names
        self.__ranker = lightgbm.LGBMRanker(
            boosting_type='gbdt',
            objective="lambdarank",
            metric="ndcg",
            n_estimators=5000,
            num_leaves=25,
            min_child_samples=300,
            device="gpu",
            verbose=-1,
        )

    def fit(self, samples_train: pd.DataFrame):
        X = samples_train[self.__feature_names]
        y = samples_train[Horse.RELEVANCE_KEY]
        qid = samples_train.groupby(Horse.RACE_ID_KEY)[Horse.RACE_ID_KEY].count()

        self.__ranker.fit(X=X, y=y, group=qid)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        X = samples_test[self.__feature_names]
        scores = self.__ranker.predict(X)

        samples_test.loc[:, "score"] = scores

        return samples_test

    @property
    def ranker(self):
        return self.__ranker

