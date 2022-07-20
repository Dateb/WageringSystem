from abc import ABC
import numpy as np
import pandas as pd
from keras import Sequential, Input, Model
from keras.callbacks import ReduceLROnPlateau
from keras.layers import Masking, LSTM, Dense, Lambda, Concatenate, \
    Normalization, LeakyReLU
from keras.metrics import MeanSquaredError
from keras.optimizers import Adam
from keras.optimizers.schedules.learning_rate_schedule import ExponentialDecay
from numpy import ndarray
from numba import cuda

from DataAbstraction.Horse import Horse
from DataAbstraction.RaceCard import RaceCard
from Estimators.custom_loss import rebalanced_kelly_loss, expected_value_loss
from SampleExtraction.FeatureManager import FeatureManager
import tensorflow as tf
tf.compat.v1.disable_eager_execution()


class NNEstimator(ABC):

    def __init__(self, label_name: str):
        self.__max_horses_per_race = 40
        self.__feature_names = FeatureManager.FEATURE_NAMES
        self.__feature_count = FeatureManager.FEATURE_COUNT
        self.__label_name = label_name

    def _init_regression_model(self):
        self._model = Sequential()
        self.__add_architecture(final_activation="linear")
        self.__set_decaying_adam_optimizer()

        self._model.compile(loss=rebalanced_kelly_loss(opportunity_loss_scale=1.0), optimizer=self.__optimizer,
                            metrics=[MeanSquaredError()])

    def _init_classification_model(self):
        self._model = Sequential()
        self.__add_architecture(final_activation="softmax")
        self.__set_adam_optimizer()

        self._model.compile(loss=expected_value_loss, optimizer=self.__optimizer)

    def __set_decaying_adam_optimizer(self):
        lr_schedule = ExponentialDecay(
            initial_learning_rate=0.000001,
            decay_rate=0.99,
            decay_steps=1000,
        )

        self.__optimizer = Adam(learning_rate=lr_schedule)

    def __set_adam_optimizer(self):
        self.__optimizer = Adam(learning_rate=0.1)

    def __add_architecture(self, final_activation: str):
        inputs = Input(shape=(self.__max_horses_per_race, self.__feature_count))
        masking = Masking(mask_value=0.0)(inputs)
        norm = Normalization()(masking)

        lstm1 = LSTM(800, return_sequences=True)(norm)
        lstm2 = LSTM(800, return_sequences=False)(lstm1)

        dense1 = Dense(2048)(lstm2)
        act1 = LeakyReLU(alpha=0.3)(dense1)
        dense2 = Dense(2048)(act1)
        act2 = LeakyReLU(alpha=0.3)(dense2)

        dense3 = Dense(1024)(act2)
        act3 = LeakyReLU(alpha=0.3)(dense3)
        dense4 = Dense(1024)(act3)
        act4 = LeakyReLU(alpha=0.3)(dense4)

        dense5 = Dense(512)(act4)
        act5 = LeakyReLU(alpha=0.3)(dense5)
        dense6 = Dense(512)(act5)
        act6 = LeakyReLU(alpha=0.3)(dense6)

        dense7 = Dense(256)(act6)
        act7 = LeakyReLU(alpha=0.3)(dense7)
        dense8 = Dense(256)(act7)
        act8 = LeakyReLU(alpha=0.3)(dense8)

        prediction = Dense(self.__max_horses_per_race, activation=final_activation)(act8)

        @tf.function
        def get_odds(tensor):
            return tensor[:, :, 0]

        odds = Lambda(get_odds)(norm)

        output = Concatenate(axis=1)([prediction, odds])

        self._model = Model(inputs=inputs, outputs=[output])
        self._model.summary()

    def _fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        x_train, y_train = self.__horse_dataframe_to_features_and_labels(samples_train)
        x_validation, y_validation = self.__horse_dataframe_to_features_and_labels(samples_validation)

        lr_callback = ReduceLROnPlateau(
            monitor="loss",
            factor=0.1,
            patience=5,
        )

        self._model.fit(
            x=x_train,
            y=y_train,
            epochs=400,
            verbose=1,
            batch_size=16,
            validation_data=(x_validation, y_validation),
            callbacks=[lr_callback],
        )

    def _transform(self, samples: pd.DataFrame) -> ndarray:
        x, y = self.__horse_dataframe_to_features_and_labels(samples)
        group_counts = samples.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        predictions = self._model.predict(x)
        scores = self.__get_non_padded_scores(predictions, group_counts)
        cuda.select_device(0)
        cuda.close()

        return scores

    def __horse_dataframe_to_features_and_labels(self, horse_dataframe: pd.DataFrame):
        horses_features = horse_dataframe[self.__feature_names].to_numpy()
        horses_win_indicator = horse_dataframe[self.__label_name].to_numpy()
        horses_odds = horse_dataframe[Horse.CURRENT_ODDS_KEY].to_numpy()
        group_counts = horse_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_horses, y_horses = self.__get_padded_features_and_labels(
            horses_features,
            horses_win_indicator,
            horses_odds,
            group_counts,
        )

        return x_horses, y_horses

    def __get_padded_features_and_labels(
            self,
            horse_features: ndarray,
            horses_win_indicator: ndarray,
            horses_odds: ndarray,
            group_counts: ndarray
    ):
        padded_horse_features = np.zeros((len(group_counts), self.__max_horses_per_race, self.__feature_count))
        padded_horse_labels = np.zeros((len(group_counts), 2 * self.__max_horses_per_race))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(self.__max_horses_per_race):
                if j < group_count:
                    padded_horse_features[i, j, :] = horse_features[horse_idx]
                    padded_horse_labels[i, j] = horses_win_indicator[horse_idx]
                    padded_horse_labels[i, self.__max_horses_per_race + j] = horses_odds[horse_idx]
                    horse_idx += 1
                else:
                    padded_horse_features[i, j, :] = 0

        return padded_horse_features, padded_horse_labels

    def __get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        for i in range(len(predictions)):
            group_count = group_counts[i]
            for j in range(group_count):
                scores[horse_idx] = predictions[i, j]
                horse_idx += 1

        return scores
