from abc import abstractmethod, ABC

import numpy as np
from numpy import ndarray


class FeaturePaddingTransformer(ABC):

    def __init__(self, padding_size_per_group: int):
        self.padding_size_per_group = padding_size_per_group

    @abstractmethod
    def transform(self, features: ndarray, group_counts: ndarray) -> ndarray:
        pass

    @abstractmethod
    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray) -> ndarray:
        pass


class FeaturePaddingTransformer3D(FeaturePaddingTransformer):

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

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray) -> ndarray:
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        num_races = len(group_counts)

        if num_races == 1:
            for j in range(group_counts[0]):
                scores[j] = predictions[j]
            return scores

        for i in range(num_races):
            group_count = group_counts[i]
            for j in range(group_count):
                scores[horse_idx] = predictions[i, j]
                horse_idx += 1

        return scores


class FeaturePaddingTransformer2D(FeaturePaddingTransformer):

    def transform(self, features: ndarray, group_counts: ndarray) -> ndarray:
        n_groups = len(group_counts)

        n_feature_values = features.shape[1]
        padded_features = np.zeros((n_groups, self.padding_size_per_group * (n_feature_values + 1)))

        group_member_idx = 0
        for i in range(n_groups):
            group_count = group_counts[i]

            for j in range(group_count):
                for k in range(n_feature_values):
                    padded_features[i, (j * n_feature_values) + k] = features[group_member_idx, k]

                group_member_idx += 1

            for j in range(group_count, self.padding_size_per_group):
                for k in range(n_feature_values):
                    padded_features[i, (j * n_feature_values) + k] = 0

        return padded_features

    def get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray) -> ndarray:
        scores = np.zeros(np.sum(group_counts))

        print(f"scores shape: {scores.shape}")
        print(f"predictions: {predictions}")

        horse_idx = 0
        score_idx = 0
        num_races = len(group_counts)

        for i in range(num_races):
            group_count = group_counts[i]
            for j in range(self.padding_size_per_group):
                if j < group_count:
                    scores[score_idx] = predictions[horse_idx]
                    score_idx += 1
                horse_idx += 1

        return scores


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
