from random import choices
from typing import List

import numpy as np
from tqdm import trange

from Estimation.Ranker import Ranker
from ModelTuning.Validator import Validator
from ModelTuning.Features.MCFeatureNode import MCFeatureNode
from ModelTuning.Features.MCFeatureTree import MCFeatureTree
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager


class FeatureSelector:

    def __init__(self, estimator: Ranker, validator: Validator):
        self.__validator = validator
        self.__estimator = estimator

        self.__base_features = [CurrentOddsExtractor().get_name()]
        self.__search_features = [
            feature for feature in FeatureManager.FEATURE_NAMES if feature not in self.__base_features
        ]

        self.__terminal_state_length = len(self.__search_features)
        self.__valid_actions = [-1, 1]
        self.__max_score = 0
        self.__best_feature_subset = []
        self.__exploration_factor = 0.2
        self.__tree = MCFeatureTree()

    def search_for_best_feature_subset(self, n_iter: int) -> List[str]:
        for i in trange(n_iter):
            front_node = self.__select()
            score, feature_subset = self.__simulate(front_node.state)
            self.__backup(front_node, score)

            if score > self.__max_score:
                self.__max_score = score
                self.__best_feature_subset = feature_subset
                print(f"Found new best subset: {self.__best_feature_subset} with score: {self.__max_score}")

        return self.__best_feature_subset

    def __select(self):
        node = self.__tree.node("root")
        while not self.__is_node_terminal(node):
            if not self.__is_node_fully_expanded(node):
                return self.__expand(node)
            else:
                node = self.__select_best_children(node)

        return node

    def __expand(self, node: MCFeatureNode):
        child_feature_idx = len(node.state)
        children = self.__tree.children(node.identifier)
        if children:
            existing_child = children[0]
            child_action = existing_child.state[child_feature_idx] * -1
            child_state = existing_child.state[:-1] + [child_action]
        else:
            node_state = node.state
            child_state = node_state + [1]

        new_node = MCFeatureNode(
            identifier=str(child_state),
            max_score=0,
            n_visits=0,
            state=child_state,
        )
        return self.__tree.add_node(new_node, node)

    def __simulate(self, node_state: List[int]):
        n_actions_left = self.__terminal_state_length - len(node_state)
        actions = choices(self.__valid_actions, k=n_actions_left)

        terminal_state = node_state + actions
        feature_subset = self.__get_feature_subset(terminal_state)
        score = self.__get_feature_subset_score(feature_subset)
        return score, feature_subset

    def __backup(self, front_node: MCFeatureNode, score: float):
        node = front_node
        while node.identifier != "root":
            node.n_visits += 1
            if score > node.max_score:
                node.max_score = score
            node = self.__tree.parent(node.identifier)
        node.n_visits += 1

    def __get_feature_subset(self, terminal_state: List[int]) -> List[str]:
        enabled_search_features = [
            self.__search_features[i] for i in range(len(self.__search_features)) if terminal_state[i] == 1
        ]
        return self.__base_features + enabled_search_features

    def __is_node_terminal(self, node: MCFeatureNode):
        return len(node.state) == self.__terminal_state_length

    def __is_node_fully_expanded(self, node):
        return len(self.__tree.children(node.identifier)) == 2

    def __select_best_children(self, node: MCFeatureNode):
        children = self.__tree.children(node.identifier)

        children_uct = np.array([self.__get_uct(node, child) for child in children])
        return children[children_uct.argmax()]

    def __get_uct(self, parent_node: MCFeatureNode, child_node: MCFeatureNode):
        exploration_value = np.sqrt(2 * np.log(parent_node.n_visits) / child_node.n_visits)
        return child_node.max_score + self.__exploration_factor * exploration_value

    def __get_feature_subset_score(self, feature_subset: List[str]) -> float:
        self.__estimator.feature_subset = feature_subset
        return self.__validator.fund_history_summary(self.__estimator, "Feature Selector").win_loss_ratio


def main():
    feature_selector = FeatureSelector()
    feature_selector.search_for_best_feature_subset(n_iter=1000)
    print('finished')


if __name__ == '__main__':
    main()
