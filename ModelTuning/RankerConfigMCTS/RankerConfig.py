import random
from copy import copy
from typing import List

import numpy as np

from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.Ranker import Ranker
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager

NUM_LEAVES_VALUES = list(np.arange(10, 80, 10))
MIN_CHILD_SAMPLES_VALUES = list(np.arange(150, 350, 50))

BASE_FEATURES = [CurrentOddsExtractor().get_name()]
SEARCH_FEATURES = [feature for feature in FeatureManager.FEATURE_NAMES if feature not in BASE_FEATURES]

N_DECISION_LIST = [len(NUM_LEAVES_VALUES), len(MIN_CHILD_SAMPLES_VALUES)] + [2 for _ in range(len(SEARCH_FEATURES))]


class RankerConfig:

    def __init__(self, decisions: List[int]):
        self.search_params = {}
        self.feature_subset = [CurrentOddsExtractor().get_name()]
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
            self.search_params["num_leaves"] = NUM_LEAVES_VALUES[decision_idx]
        if i == 1:
            self.search_params["min_child_samples"] = MIN_CHILD_SAMPLES_VALUES[decision_idx]
        if i >= 2 and decision_idx == 1:
            self.feature_subset.append(SEARCH_FEATURES[i - 2])

    def get_ranker(self) -> Ranker:
        return BoostedTreesRanker(self.feature_subset, self.search_params)

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

