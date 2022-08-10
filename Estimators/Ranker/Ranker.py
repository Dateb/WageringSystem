from abc import ABC
from typing import List, Dict

import pandas as pd

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class Ranker(ABC):

    _FIXED_PARAMS: Dict

    def __init__(self, features: List[FeatureExtractor], label_name: str):
        self._ranker = None
        self._params = None
        self.search_params = None
        self.features = features
        self.label_name = label_name

    def _fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        pass

    def transform(self, samples: pd.DataFrame) -> pd.DataFrame:
        pass

    def set_search_params(self, search_params: Dict):
        self.search_params = search_params
        self._params = {**self._FIXED_PARAMS, **search_params}
        self._ranker.set_params(**self._params)
