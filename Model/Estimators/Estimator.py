from abc import ABC, abstractmethod
from typing import Tuple

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
    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> Tuple[ndarray, float]:
        pass

    @abstractmethod
    def score_test_sample(self, test_sample: RaceCardsSample):
        pass
