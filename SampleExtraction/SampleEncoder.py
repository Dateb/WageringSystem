import numpy as np
import pandas as pd
from typing import List

from numpy import ndarray
from pandas import DataFrame

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleEncoder:

    def __init__(self, features: List[FeatureExtractor], columns: List[str]):
        self.numerical_feature_names = [feature.get_name() for feature in features if not feature.is_categorical]
        self.sample_array = None
        self.columns = columns

    def add_race_cards_arr(self, race_cards_arr: ndarray):
        if self.sample_array is None:
            self.sample_array = race_cards_arr
        else:
            self.sample_array = np.concatenate([self.sample_array, race_cards_arr])

    def delete_sample_array(self) -> None:
        self.sample_array = None

    def get_race_cards_sample(self) -> RaceCardsSample:
        race_cards_dataframe = DataFrame(data=self.sample_array, columns=self.columns)

        race_cards_dataframe[self.numerical_feature_names] = \
            race_cards_dataframe[self.numerical_feature_names].apply(pd.to_numeric, errors="coerce")

        return RaceCardsSample(race_cards_dataframe)
