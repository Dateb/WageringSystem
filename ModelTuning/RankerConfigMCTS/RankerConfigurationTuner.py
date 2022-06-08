from copy import deepcopy

import numpy as np
from tqdm import trange

from ModelTuning.RankerConfigMCTS.RankerConfig import RankerConfig
from ModelTuning.Validator import Validator
from ModelTuning.RankerConfigMCTS.RankerConfigNode import RankerConfigNode
from ModelTuning.RankerConfigMCTS.RankerConfigurationTree import RankerConfigurationTree
from Ranker.BoostedTreesRanker import BoostedTreesRanker
from Ranker.Ranker import Ranker
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor


class RankerConfigurationTuner:

    def __init__(self, validator: Validator):
        self.__validator = validator

        baseline_ranker = BoostedTreesRanker([CurrentOddsExtractor().get_name()], {})
        self.__validator.fit_ranker(baseline_ranker)
        self.__best_ranker = baseline_ranker
        self.__max_score = validator.fund_history_summary(baseline_ranker, "Ranker Tuner Baseline").win_loss_ratio
        self.__exploration_factor = 0.2
        self.__tree = RankerConfigurationTree()

    def search_for_best_ranker_config(self, max_iter_without_improvement: int) -> Ranker:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        return self.__best_ranker

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()
            ranker = self.__create_configured_ranker(front_node.ranker_config)
            score = self.__simulate(ranker)
            self.__backup(front_node, score)

            if score > self.__max_score:
                print(f"Found new best ranker: {ranker} with score: {score}")
                self.__max_score = score
                self.__best_ranker = deepcopy(ranker)
                return True

        return False

    def __select(self):
        node = self.__tree.node("root")
        while not node.ranker_config.is_terminal:
            if not self.__is_node_fully_expanded(node):
                return self.__expand(node)
            else:
                node = self.__select_best_children(node)

        return node

    def __expand(self, node: RankerConfigNode):
        next_action_idx = len(self.__tree.children(node.identifier))
        decisions_children = node.ranker_config.decisions + [next_action_idx]
        children_ranker_config = RankerConfig(decisions_children)

        new_node = RankerConfigNode(
            identifier=children_ranker_config.identifier,
            max_score=0,
            n_visits=0,
            ranker_config=children_ranker_config,
        )
        return self.__tree.add_node(new_node, node)

    def __create_configured_ranker(self, ranker_config: RankerConfig) -> Ranker:
        full_decision_list = ranker_config.get_full_decision_list()
        terminal_ranker_config = RankerConfig(full_decision_list)
        new_ranker = terminal_ranker_config.get_ranker()
        self.__validator.fit_ranker(new_ranker)
        return new_ranker

    def __simulate(self, ranker: Ranker) -> float:
        return self.__validator.fund_history_summary(ranker, "RankerConfigurationTuner").win_loss_ratio

    def __backup(self, front_node: RankerConfigNode, score: float):
        node = front_node
        while node.identifier != "root":
            node.n_visits += 1
            if score > node.max_score:
                node.max_score = score
            node = self.__tree.parent(node.identifier)
        node.n_visits += 1

    def __is_node_fully_expanded(self, node):
        return len(self.__tree.children(node.identifier)) == node.ranker_config.n_decisions_next_action

    def __select_best_children(self, node: RankerConfigNode):
        children = self.__tree.children(node.identifier)

        children_uct = np.array([self.__get_uct(node, child) for child in children])
        return children[children_uct.argmax()]

    def __get_uct(self, parent_node: RankerConfigNode, child_node: RankerConfigNode):
        exploration_value = np.sqrt(2 * np.log(parent_node.n_visits) / child_node.n_visits)
        return child_node.max_score + self.__exploration_factor * exploration_value
