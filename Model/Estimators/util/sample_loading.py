from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from numpy import ndarray
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.util.padding import FeaturePaddingTransformer, \
    ClassificationLabelPaddingTransformer, RegressionLabelPaddingTransformer
from ModelTuning import simulate_conf
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class RaceCardLoader(ABC):

    def __init__(
            self,
            sample: RaceCardsSample,
            feature_manager: FeatureManager,
            one_hot_encoder: OneHotEncoder,
            standard_scaler: StandardScaler,
            feature_padding_transformer: FeaturePaddingTransformer
    ):
        self.feature_manager = feature_manager
        self.one_hot_encoder = one_hot_encoder
        self.standard_scaler = standard_scaler

        self.feature_padding_transformer = feature_padding_transformer

        if simulate_conf.LEARNING_MODE == "Classification":
            self.label_padding_transformer = ClassificationLabelPaddingTransformer()
        else:
            self.label_padding_transformer = RegressionLabelPaddingTransformer()

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        selected_feature_names = [feature.get_name() for feature in feature_manager.search_features]

        horse_features = sample.race_cards_dataframe[selected_feature_names]
        if simulate_conf.LEARNING_MODE == "Classification":
            horse_labels = sample.race_cards_dataframe[Horse.HAS_WON_LABEL_KEY].to_numpy()
        else:
            horse_labels = sample.race_cards_dataframe[Horse.REGRESSION_LABEL_KEY].to_numpy()

        numerical_horse_features = self.standardize_numerical_features(horse_features[feature_manager.numerical_feature_names])

        one_hot_horse_features = self.one_hot_encode_cat_features(horse_features[feature_manager.categorical_feature_names])

        horse_features = np.concatenate((numerical_horse_features, one_hot_horse_features), axis=1)

        self.x = self.feature_padding_transformer.transform(horse_features, self.group_counts)
        self.y = self.label_padding_transformer.transform(horse_labels, self.group_counts)

        self.n_feature_values = horse_features.shape[1]

    @abstractmethod
    def one_hot_encode_cat_features(self, cat_horse_features: pd.DataFrame) -> ndarray:
        pass

    @abstractmethod
    def standardize_numerical_features(self, numerical_horse_features: pd.DataFrame) -> ndarray:
        pass


class TrainRaceCardLoader(RaceCardLoader):

    def standardize_numerical_features(self, numerical_horse_features: pd.DataFrame) -> ndarray:
        self.standard_scaler.fit(numerical_horse_features)
        return self.standard_scaler.transform(numerical_horse_features)

    def one_hot_encode_cat_features(self, cat_horse_features: pd.DataFrame) -> ndarray:
        self.one_hot_encoder.fit(cat_horse_features)
        return self.one_hot_encoder.transform(cat_horse_features).toarray()


class TestRaceCardLoader(RaceCardLoader):

    def standardize_numerical_features(self, numerical_horse_features: pd.DataFrame) -> ndarray:
        return self.standard_scaler.transform(numerical_horse_features)

    def one_hot_encode_cat_features(self, cat_horse_features: pd.DataFrame) -> ndarray:
        return self.one_hot_encoder.transform(cat_horse_features).toarray()
