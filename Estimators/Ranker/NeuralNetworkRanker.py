from typing import List

import pandas as pd
from keras import Input, Model
from keras.layers import Dense, Subtract, Activation, Dropout
from sklearn.preprocessing import MinMaxScaler

from Estimators.NN.LambdaRankNNCore import LambdaRankNN
from Estimators.Ranker.Ranker import Ranker
from DataAbstraction.Present.Horse import Horse


class NeuralNetworkRanker(Ranker):

    def __init__(self, feature_subset: List[str], search_params: dict):
        super().__init__(feature_subset, Horse.HAS_WON_KEY)
        self.__ranker = None
        self.__scaler = MinMaxScaler()
        self.__model = self._build_model(
            hidden_layer_sizes=(256, 128, 64),
            activation=('relu', 'relu', 'relu', 'relu', 'relu', 'relu'),
        )

    def _build_model(self, hidden_layer_sizes, activation):
        hidden_layers = []
        for i in range(len(hidden_layer_sizes)):
            hidden_layers.append(Dense(hidden_layer_sizes[i], activation=activation[i], name=str(activation[i]) + '_layer' + str(i)))
        input1 = Input(shape=(len(self.feature_subset),), name='Input_layer1')
        input2 = Input(shape=(len(self.feature_subset),), name='Input_layer2')
        x1 = input1
        x2 = input2
        for i in range(len(hidden_layer_sizes)):
            x1 = hidden_layers[i](x1)
            x1 = Dropout(rate=0.8)(x1)
            x2 = hidden_layers[i](x2)
            x2 = Dropout(rate=0.8)(x2)
        h0 = Dense(1, activation='linear', name='Identity_layer')
        x1 = h0(x1)
        x2 = h0(x2)
        subtracted = Subtract(name='Subtract_layer')([x1, x2])
        out = Activation('sigmoid', name='Activation_layer')(subtracted)
        model = Model(inputs=[input1, input2], outputs=out)
        return model

    def fit(self, samples_train: pd.DataFrame, samples_test: pd.DataFrame):
        train_features = samples_train[self.feature_subset]
        self.__scaler.fit(train_features)
        train_features = self.__scaler.transform(train_features)

        y = samples_train[Horse.RELEVANCE_KEY].to_numpy()
        qid = samples_train[Horse.RACE_ID_KEY].to_numpy()

        self.__ranker = LambdaRankNN(
            model=self.__model,
            solver='adam',
        )

        test_features = samples_test[self.feature_subset]
        test_features = self.__scaler.transform(test_features)
        test_y = samples_test[Horse.RELEVANCE_KEY].to_numpy()
        test_qid = samples_test[Horse.RACE_ID_KEY].to_numpy()

        self.__ranker.fit(train_features, y, qid, validation_data=[test_features, test_y, test_qid], epochs=500, batch_size=128)

    def transform(self, samples_test: pd.DataFrame) -> pd.DataFrame:
        test_features = samples_test[self.feature_subset]
        test_features = self.__scaler.transform(test_features)

        scores = self.__ranker.predict(test_features)

        samples_test["score"] = scores

        return samples_test

    