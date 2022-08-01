import random
from copy import copy
from typing import List

import numpy as np

from Betting.BetEvaluator import BetEvaluator
from Betting.StaticKellyBettor import StaticKellyBettor
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Estimators.Ranker.Ranker import Ranker
from ModelTuning.BetModel import BetModel
from SampleExtraction.Extractors.SpeedFigureExtractor import SpeedFigureExtractor
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager

EXPECTED_VALUE_ADDITIONAL_THRESHOLD_VALUES = list(np.arange(0.00, 0.18, 0.03))
NUM_LEAVES_VALUES = list(np.arange(20, 45, 5))
MIN_CHILD_SAMPLES_VALUES = list(np.arange(150, 350, 50))
COLSAMPLE_BYTREE_VALUES = list(np.arange(0.2, 1.2, 0.2))

BASE_FEATURES = [CurrentOddsExtractor().get_name()]
PAST_FORM_FEATURES = FeatureManager.PAST_FORM_FEATURE_NAMES
NON_PARAMETERIZED_FEATURES = [
    feature for feature in FeatureManager.NON_PARAMETERIZED_FEATURE_NAMES if feature not in BASE_FEATURES
]
SEARCH_FEATURES = PAST_FORM_FEATURES + NON_PARAMETERIZED_FEATURES

MAX_PAST_FORM_DEPTH = 10
N_DECISION_LIST = \
    [
        len(EXPECTED_VALUE_ADDITIONAL_THRESHOLD_VALUES),
        len(NUM_LEAVES_VALUES),
        len(MIN_CHILD_SAMPLES_VALUES),
        len(COLSAMPLE_BYTREE_VALUES),
        MAX_PAST_FORM_DEPTH
    ] + [2 for _ in range(len(SEARCH_FEATURES))]


class BetModelConfiguration:

    def __init__(self, decisions: List[int]):
        self.expected_value_additional_threshold = 0.0
        self.search_params = {}
        self.feature_subset = [CurrentOddsExtractor().get_name()]
        self.past_form_depth = 0
        self.decisions = decisions
        self.is_terminal = False
        if len(decisions) == len(N_DECISION_LIST):
            self.is_terminal = True
            self.__init_config()

    def __init_config(self):
        for i, decision_idx in enumerate(self.decisions):
            self.__add_ith_decision(i, decision_idx)

    def __add_ith_decision(self, i: int, decision_idx: int):
        if i == 0:
            self.expected_value_additional_threshold = EXPECTED_VALUE_ADDITIONAL_THRESHOLD_VALUES[decision_idx]
        if i == 1:
            self.search_params["num_leaves"] = NUM_LEAVES_VALUES[decision_idx]
        if i == 2:
            self.search_params["min_child_samples"] = MIN_CHILD_SAMPLES_VALUES[decision_idx]
        if i == 3:
            self.search_params["colsample_bytree"] = COLSAMPLE_BYTREE_VALUES[decision_idx]
        if i == 4:
            self.past_form_depth = decision_idx + 1
        if 5 <= i < 5 + len(PAST_FORM_FEATURES) and decision_idx == 1:
            new_past_form_features = [f"{PAST_FORM_FEATURES[i - 5]}_{k}" for k in range(1, self.past_form_depth + 1)]
            self.feature_subset += new_past_form_features
        if i >= 5 + len(PAST_FORM_FEATURES) and decision_idx == 1:
            self.feature_subset.append(NON_PARAMETERIZED_FEATURES[i - (5 + len(PAST_FORM_FEATURES))])

    def get_bet_model(self) -> BetModel:
        estimator = BoostedTreesRanker(self.feature_subset, self.search_params)

        bettor = StaticKellyBettor(self.expected_value_additional_threshold, start_kelly_wealth=1)
        bet_evaluator = BetEvaluator()

        return BetModel(estimator, bettor, bet_evaluator)

    def get_full_decision_list(self) -> List[int]:
        full_decision_list = copy(self.decisions)
        for i in range(len(self.decisions), len(N_DECISION_LIST)):
            n_decisions = N_DECISION_LIST[i]
            next_decision = random.randrange(n_decisions)
            full_decision_list.append(next_decision)
        return full_decision_list

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return N_DECISION_LIST[next_action_idx]

