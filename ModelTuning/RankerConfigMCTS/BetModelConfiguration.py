import random
from copy import copy
from typing import List

from Model.Betting.EVSingleBettor import EVSingleBettor
from Model.Estimation.BoostedTreesRanker import BoostedTreesRanker
from Model.BetModel import BetModel
from Model.Estimation.OddsShiftClassifier import OddsShiftClassifier
from Model.Probabilizing.PlaceProbabilizer import PlaceProbabilizer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModelConfiguration:
    probabilizer_values = [PlaceProbabilizer()]
    train_size_fraction_values = [1.0]
    num_boost_round_values = [400, 600, 800]
    stakes_fraction_values = [1.0]
    expected_value_additional_threshold_values = [0.0]
    lower_win_prob_threshold_values = [0]
    upper_win_prob_threshold_values = [1]
    learning_rate_values = [0.1]
    num_leaves_values = [10, 30]
    min_child_samples_values = [200]

    n_decision_list: List[int]

    def __init__(
            self,
            decisions: List[int],
            base_features: List[FeatureExtractor],
            search_features: List[FeatureExtractor],
    ):
        self.probabilizer = None
        self.train_size_fraction = 1.0
        self.num_boost_round = 0
        self.stakes_fraction = 1.0
        self.expected_value_additional_threshold = 0.0
        self.search_params = {}
        self.feature_subset: List[FeatureExtractor] = copy(base_features)
        self.search_features = search_features
        self.selected_search_features = []
        self.n_decision_list = \
            [
                len(BetModelConfiguration.probabilizer_values),
                len(BetModelConfiguration.train_size_fraction_values),
                len(BetModelConfiguration.num_boost_round_values),
                len(BetModelConfiguration.stakes_fraction_values),
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

    def __init_config(self):
        for i, decision_idx in enumerate(self.decisions):
            self.__add_ith_decision(i, decision_idx)

    def __add_ith_decision(self, i: int, decision_idx: int):
        if i == 0:
            self.probabilizer = self.probabilizer_values[decision_idx]
        if i == 1:
            self.train_size_fraction = self.train_size_fraction_values[decision_idx]
        if i == 2:
            self.num_boost_round = self.num_boost_round_values[decision_idx]
        if i == 3:
            self.stakes_fraction = self.stakes_fraction_values[decision_idx]
        if i == 4:
            self.expected_value_additional_threshold = self.expected_value_additional_threshold_values[decision_idx]
        if i == 5:
            self.lower_win_prob_threshold = self.lower_win_prob_threshold_values[decision_idx]
        if i == 6:
            self.upper_win_prob_threshold = self.upper_win_prob_threshold_values[decision_idx]
        if i == 7:
            self.search_params["learning_rate"] = self.learning_rate_values[decision_idx]
        if i == 8:
            self.search_params["num_leaves"] = self.num_leaves_values[decision_idx]
        if i == 9:
            self.search_params["min_child_samples"] = self.min_child_samples_values[decision_idx]
        if i >= 10 and decision_idx == 1:
            selected_search_feature = self.search_features[i - 10]
            self.selected_search_features.append(selected_search_feature)
            self.feature_subset.append(selected_search_feature)

    def create_bet_model(self, train_samples: RaceCardsSample) -> BetModel:
        estimator = OddsShiftClassifier(self.feature_subset, self.search_params)

        bettor = EVSingleBettor(
            self.expected_value_additional_threshold,
            self.probabilizer,
            self.stakes_fraction,
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
        config_str = f"{type(self.probabilizer).__name__}/"\
                     f"train_size_fraction: {self.train_size_fraction}/"\
                     f"stakes_fraction:{self.stakes_fraction}/"\
                     f"ev_thresh:{self.expected_value_additional_threshold}/" \
                     f"boost_rounds:{self.num_boost_round}/search_params:{self.search_params}\n"
        return config_str

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return self.n_decision_list[next_action_idx]

