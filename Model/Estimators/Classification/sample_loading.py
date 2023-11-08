import random
from abc import ABC, abstractmethod
from typing import List

import numpy as np
import torch
from numpy import ndarray
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
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
        padded_features = np.zeros((n_groups, self.padding_size_per_group, n_feature_values))

        group_member_idx = 0
        for i in range(n_groups):
            group_count = group_counts[i]

            for j in range(group_count):
                padded_features[i, j, :] = features[group_member_idx]

                group_member_idx += 1

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
            feature_padding_transformer: FeaturePaddingTransformer,
            label_padding_transformer: LabelPaddingTransformer
    ):
        self.feature_padding_transformer = feature_padding_transformer
        self.label_padding_transformer = label_padding_transformer

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

    def __init__(
            self,
            sample: RaceCardsSample,
            feature_manager: FeatureManager,
            missing_values_imputer: SimpleImputer,
            one_hot_encoder: OneHotEncoder,
            feature_padding_transformer: FeaturePaddingTransformer,
            label_padding_transformer: LabelPaddingTransformer
    ):
        super().__init__(sample, feature_padding_transformer, label_padding_transformer)

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        #TODO: Remove redundancy
        horses_features = sample.race_cards_dataframe[feature_manager.feature_names]
        if simulate_conf.LEARNING_MODE == "Classification":
            horse_labels = sample.race_cards_dataframe[Horse.CLASSIFICATION_LABEL_KEY].to_numpy()
        else:
            horse_labels = sample.race_cards_dataframe[Horse.REGRESSION_LABEL_KEY].to_numpy()

        numerical_horse_features = horses_features[feature_manager.numerical_feature_names].to_numpy()

        one_hot_encoder.fit(horses_features[feature_manager.categorical_feature_names])
        one_hot_horses_features = one_hot_encoder.transform(horses_features[feature_manager.categorical_feature_names]).toarray()

        horses_features = np.concatenate((numerical_horse_features, one_hot_horses_features), axis=1)

        # missing_values_imputer.fit(horses_features, horse_labels)
        # horses_features = missing_values_imputer.transform(horses_features)

        x = self.feature_padding_transformer.transform(horses_features, self.group_counts)
        y = self.label_padding_transformer.transform(horse_labels, self.group_counts)

        self.n_feature_values = horses_features.shape[1]
        self.dataloader = self.create_dataloader(x, y)


class TestRaceCardLoader(RaceCardLoader):

    def __init__(
            self,
            sample: RaceCardsSample,
            feature_manager: FeatureManager,
            missing_values_imputer: SimpleImputer,
            one_hot_encoder: OneHotEncoder,
            feature_padding_transformer: FeaturePaddingTransformer,
            label_padding_transformer: LabelPaddingTransformer
    ):
        super().__init__(sample, feature_padding_transformer, label_padding_transformer)

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        horses_features = sample.race_cards_dataframe[feature_manager.feature_names]
        if simulate_conf.LEARNING_MODE == "Classification":
            horse_labels = sample.race_cards_dataframe[Horse.CLASSIFICATION_LABEL_KEY].to_numpy()
        else:
            horse_labels = sample.race_cards_dataframe[Horse.REGRESSION_LABEL_KEY].to_numpy()

        numerical_horse_features = horses_features[feature_manager.numerical_feature_names].to_numpy()

        one_hot_horses_features = one_hot_encoder.transform(horses_features[feature_manager.categorical_feature_names]).toarray()

        horses_features = np.concatenate((numerical_horse_features, one_hot_horses_features), axis=1)

        # horses_features = missing_values_imputer.transform(horses_features)

        x = self.feature_padding_transformer.transform(horses_features, self.group_counts)
        y = self.label_padding_transformer.transform(horse_labels, self.group_counts)

        self.dataloader = self.create_dataloader(x, y)

        self.x_tensor = self.dataloader.dataset.tensors[0]
