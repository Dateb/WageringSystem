import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse


class SampleSet:

    def __init__(self, samples: pd.DataFrame, train_size: float = 0.8):
        self.__samples = samples

        self.__race_ids = list(self.__samples[Horse.RACE_ID_KEY].unique())
        self.__race_ids.sort()

        self.__n_races = len(self.__race_ids)
        self.__n_races_train = int(train_size * self.__n_races)
        self.__n_races_test = int((1 - train_size) * self.__n_races)

        self.__race_ids_train = self.__race_ids[:self.__n_races_train]
        self.__race_ids_test = self.__race_ids[self.__n_races_train:]

        self.__samples_train = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(self.__race_ids_train)]
        self.__samples_test = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(self.__race_ids_test)]

    @property
    def samples_train(self) -> pd.DataFrame:
        return self.__samples_train

    @property
    def samples_test(self) -> pd.DataFrame:
        return self.__samples_test

