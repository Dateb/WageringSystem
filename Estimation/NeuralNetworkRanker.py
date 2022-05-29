from typing import List

import pandas as pd
from LambdaRankNN import LambdaRankNN

from Estimation.Ranker import Ranker
from SampleExtraction.Horse import Horse


class NeuralNetworkRanker(Ranker):

    def __init__(self, feature_subset: List[str], search_params: dict):
        super().__init__(feature_subset)
        self.__ranker = None

    def fit(self, samples_train: pd.DataFrame):
        X = samples_train[self.feature_subset].to_numpy()
        y = samples_train[Horse.RELEVANCE_KEY].to_numpy()
        qid = samples_train[Horse.RACE_ID_KEY].to_numpy()

        self.__ranker = LambdaRankNN(
            input_size=X.shape[1],
            hidden_layer_sizes=(512, 256, 128, 64),
            activation=('relu', 'relu', 'relu', 'relu', ),
            solver='adam'
        )
        self.__ranker.fit(X, y, qid, epochs=5)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        X = samples_test[self.feature_subset].to_numpy()
        scores = self.__ranker.predict(X)

        samples_test["score"] = scores

        return samples_test

    