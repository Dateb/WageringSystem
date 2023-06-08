import numpy as np
import pandas as pd
from keras import Sequential, Input, Model
from keras.layers import Masking, LSTM, Dense, Lambda, Concatenate, \
    Normalization, LeakyReLU
from keras.optimizers import Adam
from numpy import ndarray
from numba import cuda

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard

from Model.Estimators.Estimator import Estimator
from ModelTuning.ModelEvaluator import ModelEvaluator
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.FeatureManager import FeatureManager
import tensorflow as tf

from SampleExtraction.RaceCardsSample import RaceCardsSample

tf.compat.v1.disable_eager_execution()


class LSTMClassifier(Estimator):

    def __init__(self, feature_manager: FeatureManager, model_evaluator: ModelEvaluator, block_splitter: BlockSplitter):
        super().__init__()
        self.max_horses_per_race = 40
        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator
        self.block_splitter = block_splitter

        self.feature_count = len(self.feature_manager.features)
        self.network = Sequential()
        self.add_architecture()

        self.network.compile(loss="MSE", optimizer=Adam(learning_rate=0.1))

    def add_architecture(self):
        print(self.feature_count)
        inputs = Input(shape=(self.max_horses_per_race, self.feature_count))
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

        prediction = Dense(self.max_horses_per_race, activation="softmax")(act8)

        self.network = Model(inputs=inputs, outputs=[prediction])
        self.network.summary()

    def predict(self, train_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        self.tune_setting(train_sample)
        self.fit(train_sample)

        x_test, _ = self.horse_dataframe_to_features_and_labels(train_sample.race_cards_dataframe)
        predictions = self.network.predict(x_test)

        #TODO: Maybe redundant calculating group_counts?
        group_counts = test_sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()
        scores = self.get_non_padded_scores(predictions, group_counts)

        return scores

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        pass

    def fit(self, train_sample: RaceCardsSample) -> None:
        x_train, y_train = self.horse_dataframe_to_features_and_labels(train_sample.race_cards_dataframe)

        self.network.fit(
            x=x_train,
            y=y_train,
            epochs=1,
            verbose=1,
            batch_size=16,
        )

    def transform(self, samples: pd.DataFrame) -> ndarray:
        x, y = self.horse_dataframe_to_features_and_labels(samples)
        group_counts = samples.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        predictions = self.network.predict(x)
        scores = self.get_non_padded_scores(predictions, group_counts)
        cuda.select_device(0)
        cuda.close()

        return scores

    def horse_dataframe_to_features_and_labels(self, horse_dataframe: pd.DataFrame):
        horses_features = horse_dataframe[self.feature_manager.feature_names].to_numpy()
        horses_win_indicator = horse_dataframe[Horse.RELEVANCE_KEY].to_numpy()
        group_counts = horse_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        x_horses, y_horses = self.get_padded_features_and_labels(
            horses_features,
            horses_win_indicator,
            group_counts,
        )

        return x_horses, y_horses

    def get_padded_features_and_labels(
            self,
            horse_features: ndarray,
            horses_win_indicator: ndarray,
            group_counts: ndarray
    ):
        padded_horse_features = np.zeros((len(group_counts), self.max_horses_per_race, self.feature_count))
        padded_horse_labels = np.zeros((len(group_counts), self.max_horses_per_race))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(self.max_horses_per_race):
                if j < group_count:
                    padded_horse_features[i, j, :] = horse_features[horse_idx]
                    padded_horse_labels[i, j] = horses_win_indicator[horse_idx]

                    horse_idx += 1
                else:
                    padded_horse_features[i, j, :] = 0
                    padded_horse_labels[i, j] = 0

        return padded_horse_features, padded_horse_labels

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(group_count):
                if j < self.max_horses_per_race:
                    scores[horse_idx] = predictions[i, j]
                else:
                    scores[horse_idx] = 0
                horse_idx += 1

        return scores
