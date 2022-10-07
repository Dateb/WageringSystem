import random
from copy import copy
from typing import List

import numpy as np

from Betting.MultiKellyBettor import MultiKellyBettor
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Model.BetModel import BetModel
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModelConfiguration:
    expected_value_additional_threshold_values = [0.5]
    num_leaves_values = [90]
    min_child_samples_values = list(np.arange(500, 550, 50))

    n_decision_list: List[int]

    def __init__(
            self,
            decisions: List[int],
            base_features: List[FeatureExtractor],
            search_features: List[FeatureExtractor],
            n_train_races: int,
    ):
        self.expected_value_additional_threshold = 0.0
        self.search_params = {}
        self.feature_subset: List[FeatureExtractor] = copy(base_features)
        self.search_features = search_features
        self.n_train_races = n_train_races
        self.selected_search_features = []
        self.n_decision_list = \
            [
                len(BetModelConfiguration.expected_value_additional_threshold_values),
                len(BetModelConfiguration.num_leaves_values),
                len(BetModelConfiguration.min_child_samples_values),
            ] + [2 for _ in range(len(search_features))]
        self.decisions = decisions
        self.is_terminal = False
        if len(decisions) == len(self.n_decision_list):
            self.is_terminal = True
            self.__init_config()

    def __init_config(self):
        for i, decision_idx in enumerate(self.decisions):
            self.__add_ith_decision(i, decision_idx)

    def __add_ith_decision(self, i: int, decision_idx: int):
        if i == 0:
            self.expected_value_additional_threshold = self.expected_value_additional_threshold_values[decision_idx]
        if i == 1:
            self.search_params["num_leaves"] = self.num_leaves_values[decision_idx]
        if i == 2:
            self.search_params["min_child_samples"] = self.min_child_samples_values[decision_idx]
        if i >= 3 and decision_idx == 1:
            selected_search_feature = self.search_features[i - 3]
            self.selected_search_features.append(selected_search_feature)
            self.feature_subset.append(selected_search_feature)

    def create_bet_model(self, train_samples: RaceCardsSample) -> BetModel:
        estimator = BoostedTreesRanker(self.feature_subset, self.search_params)

        bettor = MultiKellyBettor(self.expected_value_additional_threshold, bet_limit=20)

        bet_model = BetModel(estimator, bettor)
        bet_model.fit_estimator(train_samples.race_cards_dataframe)

        return bet_model

    def get_full_decision_list(self) -> List[int]:
        full_decision_list = copy(self.decisions)
        for i in range(len(self.decisions), len(self.n_decision_list)):
            n_decisions = self.n_decision_list[i]
            next_decision = random.randrange(n_decisions)
            full_decision_list.append(next_decision)
        return full_decision_list

    def __str__(self) -> str:
        config_str = f"{self.expected_value_additional_threshold}/{self.search_params}\n"
        for feature in self.feature_subset:
            config_str += f"{feature}\n"
        return config_str

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return self.n_decision_list[next_action_idx]

