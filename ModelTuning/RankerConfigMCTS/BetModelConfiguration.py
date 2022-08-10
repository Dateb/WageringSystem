import random
from copy import copy
from typing import List

from Betting.BetEvaluator import BetEvaluator
from Betting.StaticKellyBettor import StaticKellyBettor
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from ModelTuning.BetModel import BetModel
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor


class BetModelConfiguration:
    expected_value_additional_threshold_values: List[float]
    num_leaves_values: List[float]
    min_child_samples_values: List[float]
    colsample_by_tree_values: List[float]

    base_features: List[str]
    past_form_features: List[str]
    non_parameterized_features: List[str]
    search_features: List[str]

    max_past_form_depth: float
    n_decision_list: List[int]

    def __init__(self, decisions: List[int]):
        self.expected_value_additional_threshold = 0.0
        self.search_params = {}
        self.feature_subset = [CurrentOddsExtractor().get_name()]
        self.past_form_depth = 0
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
        if i == 3:
            self.search_params["colsample_bytree"] = self.colsample_by_tree_values[decision_idx]
        if i == 4:
            self.past_form_depth = decision_idx + 1
        if 5 <= i < 5 + len(self.past_form_features) and decision_idx == 1:
            new_past_form_features = [f"{self.past_form_features[i - 5]}_{k}" for k in range(1, self.past_form_depth + 1)]
            self.feature_subset += new_past_form_features
        if i >= 5 + len(self.past_form_features) and decision_idx == 1:
            self.feature_subset.append(self.non_parameterized_features[i - (5 + len(self.past_form_features))])

    def get_bet_model(self) -> BetModel:
        estimator = BoostedTreesRanker(self.feature_subset, self.search_params)

        bettor = StaticKellyBettor(self.expected_value_additional_threshold, start_kelly_wealth=1)
        bet_evaluator = BetEvaluator()

        return BetModel(estimator, bettor, bet_evaluator)

    def get_full_decision_list(self) -> List[int]:
        full_decision_list = copy(self.decisions)
        for i in range(len(self.decisions), len(self.n_decision_list)):
            n_decisions = self.n_decision_list[i]
            next_decision = random.randrange(n_decisions)
            full_decision_list.append(next_decision)
        return full_decision_list

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return self.n_decision_list[next_action_idx]

