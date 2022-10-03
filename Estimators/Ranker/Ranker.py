from abc import ABC
from typing import List, Dict

import pandas as pd

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class Ranker(ABC):

    _FIXED_PARAMS: Dict

    def __init__(self, features: List[FeatureExtractor], label_name: str):
        self.parameter_set = None
        self.search_params = None
        self.features = features
        self.label_name = label_name

    def _fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        pass

    def transform(self, samples: pd.DataFrame) -> pd.DataFrame:
        pass

    def set_parameter_set(self, search_params: Dict):
        self.search_params = search_params
        self.parameter_set = {**self._FIXED_PARAMS, **search_params}
