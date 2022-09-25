from typing import List, Dict

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesClassifier:

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "n_estimators": 1000,
        "verbose": -1,
        "random_state": 0,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
    }

    def __init__(self, features: List[FeatureExtractor], search_params: dict):
        self.max_horses_per_race = 40
        self.features = features
        self.label_name = Horse.HAS_WON_KEY

        if not search_params:
            search_params = {}

        self.features = features
        self.feature_names = [feature.get_name() for feature in features]
        self.classifier = LGBMClassifier()
        self.set_search_params(search_params)

    def set_search_params(self, search_params: Dict):
        self.search_params = search_params
        self._params = {**self._FIXED_PARAMS, **search_params}
        self.classifier.set_params(**self._params)

    def fit(self, samples_train: pd.DataFrame, samples_validation: pd.DataFrame):
        x_horses, y_horses = self.horse_dataframe_to_features_and_labels(samples_train)

        self.classifier.fit(X=x_horses, y=y_horses)

    def transform(self, race_cards_sample: RaceCardsSample) -> RaceCardsSample:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        x_horses, _ = self.horse_dataframe_to_features_and_labels(race_cards_dataframe)

        group_counts = race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count().to_numpy()

        predictions = self.classifier.predict(x_horses, raw_score=True)
        scores = self.__get_non_padded_scores(predictions, group_counts)

        return self.set_win_probabilities(race_cards_sample, scores)

    def set_win_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceCardsSample:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return RaceCardsSample(race_cards_dataframe)

    def horse_dataframe_to_features_and_labels(self, horse_dataframe: pd.DataFrame):
        horses_features = horse_dataframe[self.feature_names].to_numpy()
        horses_win_indicator = horse_dataframe[self.label_name].to_numpy()
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
        padded_horse_features = np.zeros((len(group_counts), self.max_horses_per_race * len(self.features)))
        padded_horse_labels = np.zeros((len(group_counts)))

        horse_idx = 0
        for i in range(len(group_counts)):
            group_count = group_counts[i]
            for j in range(self.max_horses_per_race):
                if j < group_count:
                    padded_horse_features[i, j * len(self.features):(j+1) * len(self.features)] = horse_features[horse_idx]

                    if horses_win_indicator[horse_idx] == 1:
                        padded_horse_labels[i] = j

                    horse_idx += 1
                else:
                    padded_horse_features[i, j * len(self.features):(j+1) * len(self.features)] = 0

        return padded_horse_features, padded_horse_labels

    def __get_non_padded_scores(self, predictions: ndarray, group_counts: ndarray):
        scores = np.zeros(np.sum(group_counts))

        horse_idx = 0
        for i in range(len(predictions)):
            group_count = group_counts[i]
            for j in range(group_count):
                if j < predictions.shape[1]:
                    scores[horse_idx] = predictions[i, j]
                else:
                    scores[horse_idx] = 0
                horse_idx += 1

        return scores
