import pandas as pd
import lightgbm

from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse


class BoostedTreesRanker:

    def __init__(self):
        self.__ranker = lightgbm.LGBMRanker(
            boosting_type='dart',
            objective="lambdarank",
            metric="ndcg",
            n_estimators=1000,
            max_depth=15,
        )

    def fit(self, samples_train: pd.DataFrame):
        X = samples_train[FeatureManager.FEATURE_NAMES]
        y = samples_train[Horse.RELEVANCE_KEY]
        qid = samples_train.groupby(Horse.RACE_ID_KEY)[Horse.RACE_ID_KEY].count()

        self.__ranker.fit(X=X, y=y, group=qid)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        X = samples_test[FeatureManager.FEATURE_NAMES].apply(pd.to_numeric, errors='coerce')
        scores = self.__ranker.predict(X)

        samples_test["score"] = scores

        return samples_test

    @property
    def ranker(self):
        return self.__ranker

