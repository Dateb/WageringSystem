import pandas as pd

from DataAbstraction.Present.Horse import Horse
from Estimators.NN.NNEstimator import NNEstimator


class WinProbabilityEstimator(NNEstimator):

    def __init__(self):
        super().__init__(label_name=Horse.HAS_WON_KEY)
        self._init_classification_model()

    def fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        self._fit(samples_train, samples_validation)

    def transform(self, samples: pd.DataFrame):
        scores = self._transform(samples)
        print(sum(scores))
        samples.loc[:, "win_probability"] = scores

        return samples
