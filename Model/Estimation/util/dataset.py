from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from lightgbm import Dataset


@dataclass
class HorseRacingDataset:

    lightgbm_dataset: Dataset
    categorical_feature_names: List[str]


@dataclass
class HorseData:

    features: List
    label: int


class RaceData:

    horses_data: List[HorseData]

    def __init__(self, horses_data: List[HorseData]):
        self.horses_data = horses_data
        self.positive_label_horse_idx = []
        for i in range(len(self.horses_data)):
            if horses_data[i].label:
                self.positive_label_horse_idx.append(i)


class HorseRacingSampleCreator:

    PADDING_SIZE: int = 30

    def __init__(self, feature_arr: np.ndarray, label_arr: np.ndarray, horses_per_race_counts: np.ndarray, category_indices: List[int]):
        self.races_data = []

        n_races = len(horses_per_race_counts)
        horse_idx = 0

        for i in range(n_races):
            horses_data = []
            n_horses_per_race = horses_per_race_counts[i]

            for j in range(n_horses_per_race):
                horses_data += [HorseData(list(feature_arr[horse_idx, :]), label_arr[horse_idx])]
                horse_idx += 1

            self.races_data += [RaceData(horses_data)]

        self.n_features = feature_arr.shape[1]

        # Initialize placeholder features and deduce appropriate datatypes from example features
        self.placeholder_features = [0] * self.n_features
        for idx in category_indices:
            self.placeholder_features[idx] = ""
        print(self.placeholder_features)

    def create_classification_sample(self, race_idx: int, horse_idx: int) -> Tuple[List, List]:
        n_positive_labels = len(self.races_data[race_idx].positive_label_horse_idx)
        n_horses = len(self.races_data[race_idx].horses_data)
        n_placeholder_horses = self.PADDING_SIZE - n_horses
        sample = [n_positive_labels] + self.get_horse_features(race_idx, horse_idx)

        other_horse_features = [self.get_horse_features(race_idx, i) for i in range(n_horses) if i != horse_idx]
        for horse_features in other_horse_features:
            sample += horse_features

        for _ in range(n_placeholder_horses):
            sample += self.placeholder_features

        horse_label = self.races_data[race_idx].horses_data[horse_idx].label
        return sample, [horse_label]

    def get_horse_features(self, race_idx: int, horse_idx: int) -> List:
        return self.races_data[race_idx].horses_data[horse_idx].features

    def get_n_horses_of_race(self, race_idx: int) -> int:
        return len(self.races_data[race_idx].horses_data)

    @property
    def n_races(self) -> int:
        return len(self.races_data)
