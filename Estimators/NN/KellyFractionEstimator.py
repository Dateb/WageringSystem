import pandas as pd

from DataAbstraction.Present.Horse import Horse
from Estimators.NN.NNEstimator import NNEstimator


class KellyFractionEstimator(NNEstimator):

    def __init__(self):
        super().__init__(label_name=Horse.KELLY_FRACTION_KEY)
        self._init_regression_model()

    def fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        self._fit(samples_train, samples_validation)

    def transform(self, samples: pd.DataFrame):
        scores = self._transform(samples)
        scores = scores.clip(min=0)
        print(scores)
        samples.loc[:, "stakes_fraction"] = scores

        return samples
