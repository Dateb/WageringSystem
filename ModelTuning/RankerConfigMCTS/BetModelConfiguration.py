import random
from copy import copy
from typing import List

from Model.Betting.EVSingleBettor import EVSingleBettor
from Model.Estimation.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Model.BetModel import BetModel
from Model.Probabilizing.Probabilizer import Probabilizer
from Model.Probabilizing.WinProbabilizer import WinProbabilizer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModelConfiguration:
    num_boost_round_values = [400, 600, 800]
    expected_value_additional_threshold_values = [0.0]
    lower_win_prob_threshold_values = [0]
    upper_win_prob_threshold_values = [1]
    learning_rate_values = [0.1]
    num_leaves_values = [15]
    min_child_samples_values = [200]

    n_decision_list: List[int]

    def __init__(
            self,
            decisions: List[int],
            base_features: List[FeatureExtractor],
            search_features: List[FeatureExtractor],
            n_train_races: int,
            probabilizer: Probabilizer,
    ):
        self.num_boost_round = 0
        self.expected_value_additional_threshold = 0.0
        self.search_params = {}
        self.feature_subset: List[FeatureExtractor] = copy(base_features)
        self.search_features = search_features
        self.n_train_races = n_train_races
        self.selected_search_features = []
        self.n_decision_list = \
            [
                len(BetModelConfiguration.num_boost_round_values),
                len(BetModelConfiguration.expected_value_additional_threshold_values),
                len(BetModelConfiguration.lower_win_prob_threshold_values),
                len(BetModelConfiguration.upper_win_prob_threshold_values),
                len(BetModelConfiguration.learning_rate_values),
                len(BetModelConfiguration.num_leaves_values),
                len(BetModelConfiguration.min_child_samples_values),
            ] + [2 for _ in range(len(search_features))]
        self.decisions = decisions
        self.is_terminal = False
        if len(decisions) == len(self.n_decision_list):
            self.is_terminal = True
            self.__init_config()

        self.probabilizer = probabilizer

    def __init_config(self):
        for i, decision_idx in enumerate(self.decisions):
            self.__add_ith_decision(i, decision_idx)

    def __add_ith_decision(self, i: int, decision_idx: int):
        if i == 0:
            self.num_boost_round = self.num_boost_round_values[decision_idx]
        if i == 1:
            self.expected_value_additional_threshold = self.expected_value_additional_threshold_values[decision_idx]
        if i == 2:
            self.lower_win_prob_threshold = self.lower_win_prob_threshold_values[decision_idx]
        if i == 3:
            self.upper_win_prob_threshold = self.upper_win_prob_threshold_values[decision_idx]
        if i == 4:
            self.search_params["learning_rate"] = self.learning_rate_values[decision_idx]
        if i == 5:
            self.search_params["num_leaves"] = self.num_leaves_values[decision_idx]
        if i == 6:
            self.search_params["min_child_samples"] = self.min_child_samples_values[decision_idx]
        if i >= 7 and decision_idx == 1:
            selected_search_feature = self.search_features[i - 7]
            self.selected_search_features.append(selected_search_feature)
            self.feature_subset.append(selected_search_feature)

    def create_bet_model(self, train_samples: RaceCardsSample) -> BetModel:
        estimator = BoostedTreesRanker(self.feature_subset, self.search_params)

        bettor = EVSingleBettor(
            self.expected_value_additional_threshold,
            self.probabilizer,
        )

        bet_model = BetModel(estimator, self.probabilizer, bettor)
        bet_model.fit_estimator(train_samples.race_cards_dataframe, self.num_boost_round)

        return bet_model

    def get_full_decision_list(self) -> List[int]:
        full_decision_list = copy(self.decisions)
        for i in range(len(self.decisions), len(self.n_decision_list)):
            n_decisions = self.n_decision_list[i]
            next_decision = random.randrange(n_decisions)
            full_decision_list.append(next_decision)
        return full_decision_list

    def __str__(self) -> str:
        config_str = f"{self.expected_value_additional_threshold}/" \
                     f"{self.lower_win_prob_threshold}-{self.upper_win_prob_threshold}/" \
                     f"{self.num_boost_round}/{self.search_params}\n"
        return config_str

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return self.n_decision_list[next_action_idx]

