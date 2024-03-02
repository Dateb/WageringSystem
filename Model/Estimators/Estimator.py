from abc import ABC, abstractmethod
from typing import Tuple

from Model.Estimators.estimated_probabilities_creation import EstimationResult
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Estimator(ABC):

    def __init__(self, feature_manager: FeatureManager):
        self.feature_manager = feature_manager

    @abstractmethod
    def predict(self, sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        pass

    def fit(self, train_sample: RaceCardsSample) -> float:
        pass

    def score_test_sample(self, test_sample: RaceCardsSample):
        pass
