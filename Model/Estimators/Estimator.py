from abc import ABC, abstractmethod

import pandas as pd
from numpy import ndarray

from SampleExtraction.RaceCardsSample import RaceCardsSample


class Estimator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def predict(self, train_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        pass

    @abstractmethod
    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    @abstractmethod
    def fit(self, train_sample: RaceCardsSample) -> None:
        pass
