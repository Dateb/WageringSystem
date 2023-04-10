import numpy as np
import pandas as pd
from typing import List

from numpy import ndarray
from pandas import DataFrame

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager, columns: List[str]):
        self.feature_names = feature_manager.feature_names
        self.__samples_array = None
        self.__columns = columns

    def add_race_cards_arr(self, race_cards_arr: ndarray):
        if self.__samples_array is None:
            self.__samples_array = race_cards_arr
        else:
            self.__samples_array = np.concatenate([self.__samples_array, race_cards_arr])

    def get_race_cards_sample(self) -> RaceCardsSample:
        print(self.__columns)
        race_cards_dataframe = DataFrame(data=self.__samples_array, columns=self.__columns)

        print("dataframe created")
        # race_cards_dataframe[self.feature_names] = race_cards_dataframe[self.feature_names].astype(np.float32)

        print("dataframe made to numeric")
        return RaceCardsSample(race_cards_dataframe)
