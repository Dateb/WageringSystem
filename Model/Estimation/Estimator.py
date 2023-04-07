from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
from numpy import ndarray

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


@dataclass
class ClassificationResult:

    y_true: ndarray
    y_pred: ndarray
    shift: ndarray


class Estimator(ABC):

    _FIXED_PARAMS: Dict

    def __init__(self, features: List[FeatureExtractor], label_name: str):
        self.parameter_set = None
        self.search_params = None
        self.features = features
        self.label_name = label_name

    @abstractmethod
    def fit(self, samples_train: pd.DataFrame, num_boost_round: int):
        pass

    @abstractmethod
    def score_test_races(self, race_cards_sample: RaceCardsSample) -> ClassificationResult:
        pass

    def set_parameter_set(self, search_params: Dict):
        self.search_params = search_params
        self.parameter_set = {**self._FIXED_PARAMS, **search_params}
