import random
from abc import ABC
from typing import List

import numpy as np
import torch
from numpy import ndarray
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from torch.utils.data import DataLoader, TensorDataset

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class RaceCardLoader(ABC):

    def __init__(self, sample: RaceCardsSample, horses_per_race_padding_size: int):
        self.horses_per_race_padding_size = horses_per_race_padding_size

    def create_dataloader(self, x: ndarray, y: ndarray) -> DataLoader:
        tensor_x = torch.Tensor(x)
        tensor_y = torch.Tensor(y).type(torch.LongTensor)

        dataset = TensorDataset(tensor_x, tensor_y)

        return DataLoader(dataset, batch_size=256, shuffle=True)

    def get_padded_features_and_labels(
            self,
            horse_features: ndarray,
            horses_win_indicator: ndarray,
            group_counts: ndarray,
            n_permutations_per_race: int,
            shuffle_horse_values: bool = True
    ):
        n_feature_values = horse_features.shape[1]
        padded_horse_features = np.zeros((len(group_counts), self.horses_per_race_padding_size, n_feature_values))
        padded_horse_labels = np.zeros((len(group_counts)))

        print(len(group_counts))
        print(sum(horses_win_indicator))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]

            for j in range(group_count):
                padded_horse_features[i, j, :] = horse_features[horse_idx]
                if horses_win_indicator[horse_idx]:
                    padded_horse_labels[i] = j

                horse_idx += 1

        return padded_horse_features, padded_horse_labels


class TrainRaceCardLoader(RaceCardLoader):

    def __init__(self, sample: RaceCardsSample, feature_manager: FeatureManager, horses_per_race_padding_size: int,
                 missing_values_imputer: SimpleImputer, one_hot_encoder: OneHotEncoder):
        super().__init__(sample, horses_per_race_padding_size)

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        #TODO: Remove redundancy
        horses_features = sample.race_cards_dataframe[feature_manager.feature_names]
        horses_win_indicator = sample.race_cards_dataframe[Horse.LABEL_KEY].to_numpy()

        numerical_horse_features = horses_features[feature_manager.numerical_feature_names].to_numpy()

        one_hot_encoder.fit(horses_features[feature_manager.categorical_feature_names])
        one_hot_horses_features = one_hot_encoder.transform(horses_features[feature_manager.categorical_feature_names]).toarray()

        horses_features = np.concatenate((numerical_horse_features, one_hot_horses_features), axis=1)

        # missing_values_imputer.fit(horses_features, horses_win_indicator)
        # horses_features = missing_values_imputer.transform(horses_features)

        x, y = self.get_padded_features_and_labels(
            horses_features,
            horses_win_indicator,
            self.group_counts,
            n_permutations_per_race=1,
            shuffle_horse_values=False,
        )

        self.n_feature_values = horses_features.shape[1]
        self.dataloader = self.create_dataloader(x, y)


class TestRaceCardLoader(RaceCardLoader):

    def __init__(self, sample: RaceCardsSample, feature_manager: FeatureManager, horses_per_race_padding_size: int,
                 missing_values_imputer: SimpleImputer, one_hot_encoder: OneHotEncoder):
        super().__init__(sample, horses_per_race_padding_size)

        self.group_counts = sample.race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY, sort=True)[
            RaceCard.RACE_ID_KEY].count().to_numpy()

        horses_features = sample.race_cards_dataframe[feature_manager.feature_names]
        horses_win_indicator = sample.race_cards_dataframe[Horse.LABEL_KEY].to_numpy()

        numerical_horse_features = horses_features[feature_manager.numerical_feature_names].to_numpy()

        one_hot_horses_features = one_hot_encoder.transform(horses_features[feature_manager.categorical_feature_names]).toarray()

        horses_features = np.concatenate((numerical_horse_features, one_hot_horses_features), axis=1)

        # horses_features = missing_values_imputer.transform(horses_features)

        x, y = self.get_padded_features_and_labels(
            horses_features,
            horses_win_indicator,
            self.group_counts,
            n_permutations_per_race=1,
            shuffle_horse_values=False
        )

        self.dataloader = self.create_dataloader(x, y)

        self.x_tensor = self.dataloader.dataset.tensors[0]
