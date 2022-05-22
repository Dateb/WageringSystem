import random
from typing import Tuple

import pandas as pd
from SampleExtraction.Horse import Horse


class SampleSet:

    def __init__(self, samples: pd.DataFrame, train_size: float = 0.75):
        self.__samples = samples

        self.__race_ids = list(self.__samples[Horse.RACE_ID_KEY].unique())
        print(self.__race_ids)

        self.__n_races = len(self.__race_ids)
        self.__n_races_train = int(train_size * self.__n_races)

    def create_split(self, random_state: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        random.seed(random_state)
        race_ids_train = random.sample(self.__race_ids, self.__n_races_train)
        race_ids_test = [race_id for race_id in self.__race_ids if race_id not in race_ids_train]

        samples_train = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(race_ids_train)]
        samples_test = self.__samples[self.__samples[Horse.RACE_ID_KEY].isin(race_ids_test)]

        return samples_train, samples_test

