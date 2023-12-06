from abc import abstractmethod

import numpy as np
from numpy import ndarray


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
