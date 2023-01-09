import numpy as np
import pandas as pd
from typing import List

from numpy import ndarray
from pandas import DataFrame

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleEncoder:

    def __init__(self, features: List[FeatureExtractor], columns: List[str]):
        self.__feature_names = [feature.get_name() for feature in features]
        self.__samples_array = None
        self.__columns = columns

    def add_race_cards_arr(self, race_cards_arr: ndarray):
        if self.__samples_array is None:
            self.__samples_array = race_cards_arr
        else:
            self.__samples_array = np.concatenate([self.__samples_array, race_cards_arr])

    def get_race_cards_sample(self) -> RaceCardsSample:
        race_cards_dataframe = DataFrame(data=self.__samples_array, columns=self.__columns)

        race_cards_dataframe[self.__feature_names] = \
            race_cards_dataframe[self.__feature_names].apply(pd.to_numeric, errors="coerce")

        race_cards_dataframe[Horse.CURRENT_ESTIMATION_WIN_ODDS_KEY] = \
            race_cards_dataframe[Horse.CURRENT_ESTIMATION_WIN_ODDS_KEY].apply(pd.to_numeric, errors="coerce")

        return RaceCardsSample(race_cards_dataframe)
