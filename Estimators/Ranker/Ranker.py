from abc import ABC
from typing import List, Dict

import pandas as pd


class Ranker(ABC):

    _FIXED_PARAMS: Dict

    def __init__(self, feature_subset: List[str], label_name: str):
        self._ranker = None
        self._params = None
        self._search_params = None
        self.feature_subset = feature_subset
        self.label_name = label_name

    def _fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        pass

    def transform(self, samples: pd.DataFrame) -> pd.DataFrame:
        pass

    def set_search_params(self, search_params: Dict):
        self._search_params = search_params
        self._params = {**self._FIXED_PARAMS, **search_params}
        self._ranker.set_params(**self._params)

    def __str__(self) -> str:
        return f"{self._search_params}/{self.feature_subset}"

