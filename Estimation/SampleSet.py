import random
from typing import Tuple

import pandas as pd
from SampleExtraction.Horse import Horse


class SampleSet:

    def __init__(self, samples: pd.DataFrame, train_size: float = 0.75):
        self.__samples = samples

        self.__race_ids = list(self.__samples[Horse.RACE_ID_KEY].unique())
        self.__race_ids.sort()

        self.__n_races = len(self.__race_ids)
        self.__n_races_train = int(train_size * self.__n_races)
        self.__n_races_test = int((1 - train_size) * self.__n_races)

        race_ids_train = self.__race_ids[:self.__n_races_train]
        self.__samples_train = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(race_ids_train)]

        self.__race_ids_test = self.__race_ids[self.__n_races_train:]

    def create_split(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        samples_test = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(self.__race_ids_test)]

        return self.__samples_train, samples_test

    @property
    def samples_train(self) -> pd.DataFrame:
        return self.__samples_train

