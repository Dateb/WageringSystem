from typing import List
import numpy as np
import pandas as pd
from numpy import ndarray
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import LSTM, Dense, Masking
from numba import cuda
from tensorflow.python.keras.losses import MeanSquaredError
from tensorflow.python.keras.optimizer_v2.adam import Adam
from tensorflow.python.keras.optimizer_v2.learning_rate_schedule import ExponentialDecay

from DataAbstraction.RaceCard import RaceCard
from DataAbstraction.Horse import Horse
from Estimators.custom_loss import rebalanced_kelly_loss
from SampleExtraction.FeatureManager import FeatureManager


class NNEstimator:

    def __init__(self):
        self.__max_horses_per_race = 40
        self._feature_names = FeatureManager.FEATURE_NAMES
        self.__feature_count = FeatureManager.FEATURE_COUNT

        self.__init__model()

    def __init__model(self):
        self._model = Sequential()
        self._model.add(Masking(mask_value=0, input_shape=(self.__max_horses_per_race, self.__feature_count)))

        self._model.add(LSTM(100, activation='relu', return_sequences=True))
        self._model.add(LSTM(100, activation='relu', return_sequences=True))
        self._model.add(LSTM(100, activation='relu', return_sequences=False))
        self._model.add(Dense(1024, activation='relu'))
        self._model.add(Dense(512, activation='relu'))
        self._model.add(Dense(512, activation='relu'))
        self._model.add(Dense(512, activation='relu'))
        self._model.add(Dense(256, activation='relu'))
        self._model.add(Dense(256, activation='relu'))
        self._model.add(Dense(128, activation='relu'))
        self._model.add(Dense(64, activation='relu'))
        self._model.add(Dense(self.__max_horses_per_race, activation='linear'))

        lr_schedule = ExponentialDecay(
            initial_learning_rate=0.01,
            decay_rate=0.98,
            decay_steps=284,
        )
        opt = Adam(learning_rate=lr_schedule)
        self._model.compile(loss=rebalanced_kelly_loss(opportunity_loss_scale=1.0), optimizer=opt, metrics=[MeanSquaredError()])

    def fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        horse_features_train = samples_train[self._feature_names].to_numpy()
        horse_labels_train = samples_train[Horse.KELLY_FRACTION_KEY].to_numpy()
        group_counts_train = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_train, y_train = self.get_padded_features_and_labels(
            horse_features_train,
            horse_labels_train,
            group_counts_train,
        )

        horse_features_validation = samples_validation[self._feature_names].to_numpy()
        horse_labels_validation = samples_validation[Horse.KELLY_FRACTION_KEY].to_numpy()
        group_counts_validation = samples_validation.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_validation, y_validation = self.get_padded_features_and_labels(
            horse_features_validation,
            horse_labels_validation,
            group_counts_validation,
        )

        self._model.fit(
            x=x_train,
            y=y_train,
            epochs=2,
            verbose=1,
            batch_size=64,
            validation_data=(x_validation, y_validation),
        )

    def get_padded_features_and_labels(self, horse_features: ndarray, horse_labels: ndarray, group_counts: ndarray):
        padded_horse_features = np.zeros((len(group_counts), self.__max_horses_per_race, self.__feature_count))
        padded_horse_labels = np.zeros((len(group_counts), self.__max_horses_per_race))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(self.__max_horses_per_race):
                if j < group_count:
                    padded_horse_features[i, j, :] = horse_features[horse_idx]
                    padded_horse_labels[i, j] = horse_labels[horse_idx]
                    horse_idx += 1
                else:
                    padded_horse_features[i, j, :] = 0

        return padded_horse_features, padded_horse_labels

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray, n_horses: int):
        scores = np.zeros(n_horses)

        horse_idx = 0
        for i in range(len(predictions)):
            group_count = group_counts[i]
            for j in range(group_count):
                scores[horse_idx] = predictions[i, j]
                horse_idx += 1

        return scores

    def transform(self, samples: pd.DataFrame) -> pd.DataFrame:
        horse_features = samples[self._feature_names].to_numpy()
        horse_labels = samples[Horse.KELLY_FRACTION_KEY].to_numpy()
        group_counts = samples.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_test, _ = self.get_padded_features_and_labels(horse_features, horse_labels, group_counts)

        predictions = self._model.predict(x_test)
        scores = self.get_non_padded_scores(predictions, group_counts, len(samples))
        cuda.select_device(0)
        cuda.close()

        scores = scores.clip(min=0)
        print(scores)

        samples.loc[:, "stakes_fraction"] = scores

        return samples
