from typing import List

import numpy as np
import pandas as pd
from lightgbm import LGBMRanker
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import LSTM, Dense, Masking
from numba import cuda
from tensorflow.python.keras.losses import MeanSquaredError
from tensorflow.python.keras.optimizer_v2.adam import Adam
from tensorflow.python.keras.optimizer_v2.learning_rate_schedule import ExponentialDecay

from DataAbstraction.RaceCard import RaceCard
from DataAbstraction.Horse import Horse

from Estimators.Ranker import Ranker
from Estimators.custom_loss import rebalanced_kelly_loss
from SampleExtraction.FeatureManager import FeatureManager


class KellyFractionEstimator(Ranker):

    def __init__(self, feature_subset: List[str], search_params: dict):
        super().__init__(feature_subset)

        self.__max_horses_per_race = 40
        self.__feature_count = FeatureManager.FEATURE_COUNT
        self.__init__model()

    def __init__model(self):
        self.__model = Sequential()
        self.__model.add(Masking(mask_value=0, input_shape=(self.__max_horses_per_race, self.__feature_count)))

        self.__model.add(LSTM(100, activation='relu', return_sequences=True))
        self.__model.add(LSTM(100, activation='relu', return_sequences=True))
        self.__model.add(LSTM(100, activation='relu', return_sequences=False))
        self.__model.add(Dense(1024, activation='relu'))
        self.__model.add(Dense(512, activation='relu'))
        self.__model.add(Dense(512, activation='relu'))
        self.__model.add(Dense(512, activation='relu'))
        self.__model.add(Dense(256, activation='relu'))
        self.__model.add(Dense(256, activation='relu'))
        self.__model.add(Dense(128, activation='relu'))
        self.__model.add(Dense(64, activation='relu'))
        self.__model.add(Dense(self.__max_horses_per_race, activation='linear'))

        lr_schedule = ExponentialDecay(
            initial_learning_rate=0.01,
            decay_rate=0.98,
            decay_steps=284,
        )
        opt = Adam(learning_rate=lr_schedule)
        self.__model.compile(loss=rebalanced_kelly_loss(opportunity_loss_scale=1.0), optimizer=opt, metrics=[MeanSquaredError()])

    def fit(self, samples_train: pd.DataFrame):
        horse_train = samples_train[self.feature_subset].to_numpy()
        label_train = samples_train[Horse.KELLY_FRACTION_KEY]
        group_count_vec = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_train = np.zeros((len(group_count_vec), self.__max_horses_per_race, self.__feature_count))
        y_train = np.zeros((len(group_count_vec), self.__max_horses_per_race))

        horse_idx = 0
        for i in range(len(group_count_vec)):
            group_count = group_count_vec[i]
            for j in range(self.__max_horses_per_race):
                if j < group_count:
                    x_train[i, j, :] = horse_train[horse_idx]
                    y_train[i, j] = label_train[horse_idx]
                    horse_idx += 1
                else:
                    x_train[i, j, :] = 0

        self.__model.fit(x_train, y_train, epochs=50, validation_split=0.2, verbose=1, batch_size=64)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        horse_test = samples_test[self.feature_subset].to_numpy()
        n_test_horses = len(samples_test)
        group_count_vec = samples_test.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()
        x_test = np.zeros((len(group_count_vec), self.__max_horses_per_race, self.__feature_count))

        horse_idx = 0
        for i in range(len(group_count_vec)):
            group_count = group_count_vec[i]
            for j in range(self.__max_horses_per_race):
                if j < group_count:
                    x_test[i, j, :] = horse_test[horse_idx]
                    horse_idx += 1
                else:
                    x_test[i, j, :] = 0

        pred = self.__model.predict(x_test)
        cuda.select_device(0)
        cuda.close()

        scores = np.zeros(n_test_horses)

        horse_idx = 0
        for i in range(len(group_count_vec)):
            group_count = group_count_vec[i]
            for j in range(group_count):
                scores[horse_idx] = pred[i, j]
                horse_idx += 1

        scores = scores.clip(min=0)
        print(scores)

        samples_test.loc[:, "stakes_fraction"] = scores

        return samples_test

    @property
    def ranker(self):
        return self._ranker

