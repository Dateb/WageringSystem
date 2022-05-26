from random import choices
from typing import List

import numpy as np
from tqdm import trange
from treelib import Tree, Node

from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.SampleSet import SampleSet
from Experiments.ValidationScorer import ValidationScorer
from Experiments.Validator import Validator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder


class FeatureSelector:

    def __init__(self):
        self.__raw_races = RaceCardsPersistence("train_race_cards").load_raw()
        race_cards = [
            RaceCard(race_id, self.__raw_races[race_id], remove_non_starters=False) for race_id in self.__raw_races
        ]

        sample_encoder = SampleEncoder(FeatureManager())
        samples = sample_encoder.transform(race_cards)
        self.__sample_set = SampleSet(samples)
        self.__bettor = WinBettor(kelly_wealth=1000)

        self.__base_features = [CurrentOddsExtractor().get_name()]
        self.__search_features = [
            feature for feature in FeatureManager.FEATURE_NAMES if feature not in self.__base_features
        ]

        self.__terminal_state_length = len(self.__search_features)
        self.__valid_actions = [-1, 1]
        self.__max_score = 0
        self.__best_feature_subset = []
        self.__exploration_factor = 0.5
        self.__init_tree()

    def __init_tree(self):
        self.__tree = Tree()
        self.__tree.create_node(identifier="root", data={"state": [], "n_visits": 0, "max_score": 0})

    def run(self, n_iter: int):
        for i in trange(n_iter):
            front_node = self.__select()
            score, feature_subset = self.__simulate(front_node.data["state"])
            self.__backup(front_node, score)

            if score > self.__max_score:
                self.__max_score = score
                self.__best_feature_subset = feature_subset
                print(f"Found new best subset: {self.__best_feature_subset} with score: {self.__max_score}")

    def __select(self):
        node = self.__tree.get_node("root")
        while not self.__is_node_terminal(node):
            if not self.__is_node_fully_expanded(node):
                return self.__expand(node)
            else:
                node = self.__select_best_children(node)

        return node

    def __expand(self, node):
        child_feature_idx = self.__tree.depth(node.identifier)
        children = self.__tree.children(node.identifier)
        if children:
            child = children[0]
            child_state = child.data["state"]
            other_child_action = child_state[child_feature_idx] * -1
            other_child_state = child_state[:-1] + [other_child_action]
            return self.__tree.create_node(identifier=str(other_child_state), parent=node, data={"state": other_child_state, "n_visits": 0, "max_score": 0})
        else:
            node_state = node.data["state"]
            child_state = node_state + [1]
            return self.__tree.create_node(identifier=str(child_state), parent=node, data={"state": child_state, "n_visits": 0, "max_score": 0})

    def __simulate(self, node_state: List[int]):
        n_actions_left = self.__terminal_state_length - len(node_state)
        actions = choices(self.__valid_actions, k=n_actions_left)

        terminal_state = node_state + actions
        feature_subset = self.__get_feature_subset(terminal_state)
        score = self.__get_feature_subset_score(feature_subset)
        return score, feature_subset

    def __backup(self, front_node: Node, score: float):
        node = front_node
        while node is not None:
            node.data["n_visits"] += 1
            if score > node.data["max_score"]:
                node.data["max_score"] = score
            node = self.__tree.parent(node.identifier)

    def __get_feature_subset(self, terminal_state: List[int]) -> List[str]:
        enabled_search_features = [
            self.__search_features[i] for i in range(len(self.__search_features)) if terminal_state[i] == 1
        ]
        return self.__base_features + enabled_search_features

    def __is_node_terminal(self, node):
        return len(node.data["state"]) == self.__terminal_state_length

    def __is_node_fully_expanded(self, node):
        return len(self.__tree.children(node.identifier)) == 2

    def __select_best_children(self, node):
        children = self.__tree.children(node.identifier)

        children_uct = np.array([self.__get_uct(node, child) for child in children])
        return children[children_uct.argmax()]

    def __get_uct(self, parent_node, child_node):
        n_visits_parent = parent_node.data["n_visits"]
        n_visits_child = child_node.data["n_visits"]
        exploration_value = np.sqrt(2 * np.log(n_visits_parent) / n_visits_child)
        return child_node.data["max_score"] + self.__exploration_factor * exploration_value

    def __get_feature_subset_score(self, feature_subset: List[str]) -> float:
        estimator = BoostedTreesRanker(feature_subset, search_params={})
        validator = Validator(estimator, self.__bettor, self.__sample_set, self.__raw_races)
        validation_scorer = ValidationScorer(validator)

        return validation_scorer.score()


def main():
    feature_selector = FeatureSelector()
    feature_selector.run(n_iter=10000)
    print('finished')


if __name__ == '__main__':
    main()
