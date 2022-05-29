from abc import ABC
from typing import List

import pandas as pd


class Ranker(ABC):

    def __init__(self, feature_subset: List[str]):
        self.feature_subset = feature_subset

    def fit(self, samples_train: pd.DataFrame):
        pass

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        pass

