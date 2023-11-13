from abc import ABC, abstractmethod

from numpy import ndarray

from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Estimator(ABC):

    def __init__(self, feature_manager: FeatureManager):
        self.feature_manager = feature_manager

    @abstractmethod
    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        pass

    @abstractmethod
    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        pass

    @abstractmethod
    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    @abstractmethod
    def fit(self, train_sample: RaceCardsSample) -> None:
        pass
