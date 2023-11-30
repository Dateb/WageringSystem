import random
from abc import ABC, abstractmethod
from typing import List

import numpy as np
import pandas as pd
import torch
from numpy import ndarray
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning import simulate_conf
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class FeaturePaddingTransformer:

    def __init__(self, padding_size_per_group: int):
        self.padding_size_per_group = padding_size_per_group

    def transform(self, features: ndarray, group_counts: ndarray) -> ndarray:
        n_groups = len(group_counts)

        n_feature_values = features.shape[1]
        padded_features = np.zeros((n_groups, self.padding_size_per_group, n_feature_values + 1))

        group_member_idx = 0
        for i in range(n_groups):
            group_count = group_counts[i]

            for j in range(group_count):
                padded_features[i, j, :] = np.concatenate([features[group_member_idx], [0]])

                group_member_idx += 1

            for j in range(group_count, self.padding_size_per_group):
                padded_features[i, j, n_feature_values] = 1

        return padded_features


class LabelPaddingTransformer:

    def __init__(self):
        pass

    @abstractmethod
    def transform(self, labels: ndarray, group_counts: ndarray) -> ndarray:
        pass


class ClassificationLabelPaddingTransformer(LabelPaddingTransformer):

    def __init__(self):
        super().__init__()

    def transform(self, labels: ndarray, group_counts: ndarray) -> ndarray:
        n_groups = len(group_counts)
        padded_labels = np.zeros(n_groups)

        group_member_idx = 0
        for i in range(n_groups):
            group_count = group_counts[i]

            for j in range(group_count):
                if labels[group_member_idx]:
                    padded_labels[i] = j

                group_member_idx += 1

        return padded_labels


class RegressionLabelPaddingTransformer(LabelPaddingTransformer):

    def __init__(self):
        super().__init__()

    def transform(self, labels: ndarray, group_counts: ndarray) -> ndarray:
        n_groups = len(group_counts)
        padded_labels = np.zeros((n_groups, 20), dtype=float)

        group_member_idx = 0
        for i in range(n_groups):
            group_count = group_counts[i]

            for j in range(group_count):
                padded_labels[i, j] = labels[group_member_idx]
                group_member_idx += 1

        return padded_labels


class RaceCardLoader(ABC):

    def __init__(
            self,
            sample: RaceCardsSample,
            feature_manager: FeatureManager,
            one_hot_encoder: OneHotEncoder,
            standard_scaler: StandardScaler,
            feature_padding_transformer: FeaturePaddingTransformer,
            label_padding_transformer: LabelPaddingTransformer
    ):
        self.feature_manager = feature_manager
        self.one_hot_encoder = one_hot_encoder
        self.standard_scaler = standard_scaler
        self.feature_padding_transformer = feature_padding_transformer
        self.label_padding_transformer = label_padding_transformer

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        selected_feature_names = [feature.get_name() for feature in feature_manager.search_features]

        horse_features = sample.race_cards_dataframe[selected_feature_names]
        if simulate_conf.LEARNING_MODE == "Classification":
            horse_labels = sample.race_cards_dataframe[Horse.CLASSIFICATION_LABEL_KEY].to_numpy()
        else:
            horse_labels = sample.race_cards_dataframe[Horse.REGRESSION_LABEL_KEY].to_numpy()

        numerical_horse_features = self.standardize_numerical_features(horse_features[feature_manager.numerical_feature_names])

        one_hot_horse_features = self.one_hot_encode_cat_features(horse_features[feature_manager.categorical_feature_names])

        horse_features = np.concatenate((numerical_horse_features, one_hot_horse_features), axis=1)

        x = self.feature_padding_transformer.transform(horse_features, self.group_counts)
        y = self.label_padding_transformer.transform(horse_labels, self.group_counts)

        self.n_feature_values = horse_features.shape[1]
        self.dataloader = self.create_dataloader(x, y)

    @abstractmethod
    def one_hot_encode_cat_features(self, cat_horse_features: pd.DataFrame) -> ndarray:
        pass

    @abstractmethod
    def standardize_numerical_features(self, numerical_horse_features: pd.DataFrame) -> ndarray:
        pass

    def create_dataloader(self, x: ndarray, y: ndarray) -> DataLoader:
        tensor_x = torch.Tensor(x)

        if simulate_conf.LEARNING_MODE == "Classification":
            label_dtype = torch.LongTensor
        else:
            label_dtype = torch.FloatTensor

        tensor_y = torch.Tensor(y).type(label_dtype)

        dataset = TensorDataset(tensor_x, tensor_y)

        return DataLoader(dataset, batch_size=256, shuffle=True)


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
