from copy import deepcopy
from typing import Dict

import numpy as np
from pandas import DataFrame
from tqdm import trange

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.BetModel import BetModel
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTree import BetModelConfigurationTree


class BetModelConfigurationTuner:

    def __init__(self, race_cards: Dict[str, RaceCard], train_samples: DataFrame, validation_samples: DataFrame):
        self.__race_cards = race_cards
        self.__train_samples = train_samples
        self.__validation_samples = validation_samples

        self.__best_bet_model = None
        self.__max_score = -np.Inf
        self.__exploration_factor = 0.1
        self.__tree = BetModelConfigurationTree()

    def search_for_best_configuration(self, max_iter_without_improvement: int) -> BetModel:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        return self.__best_bet_model

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()
            bet_model = self.__create_configured_bet_model(front_node.ranker_config)
            score = self.__simulate(bet_model)
            self.__backup(front_node, score)

            if score > self.__max_score:
                print(f"Score: {score}, Setup: {bet_model} ")
                self.__max_score = score
                self.__best_bet_model = deepcopy(bet_model)
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

    def __expand(self, node: BetModelConfigurationNode):
        next_action_idx = len(self.__tree.children(node.identifier))
        decisions_children = node.ranker_config.decisions + [next_action_idx]
        children_ranker_config = BetModelConfiguration(decisions_children)

        new_node = BetModelConfigurationNode(
            identifier=children_ranker_config.identifier,
            max_score=0,
            n_visits=0,
            ranker_config=children_ranker_config,
        )
        return self.__tree.add_node(new_node, node)

    def __create_configured_bet_model(self, ranker_config: BetModelConfiguration) -> BetModel:
        full_decision_list = ranker_config.get_full_decision_list()
        terminal_ranker_config = BetModelConfiguration(full_decision_list)
        new_bet_model = terminal_ranker_config.get_bet_model()
        new_bet_model.fit_estimator(self.__train_samples, self.__validation_samples)
        return new_bet_model

    def __simulate(self, bet_model: BetModel) -> float:
        return bet_model.fund_history_summary(self.__race_cards, self.__validation_samples, "RankerConfigurationTuner").validation_score

    def __backup(self, front_node: BetModelConfigurationNode, score: float):
        node = front_node
        while node.identifier != "root":
            node.n_visits += 1
            if score > node.max_score:
                node.max_score = score
            node = self.__tree.parent(node.identifier)
        node.n_visits += 1

    def __is_node_fully_expanded(self, node):
        return len(self.__tree.children(node.identifier)) == node.ranker_config.n_decisions_next_action

    def __select_best_children(self, node: BetModelConfigurationNode):
        children = self.__tree.children(node.identifier)

        children_uct = np.array([self.__get_uct(node, child) for child in children])
        return children[children_uct.argmax()]

    def __get_uct(self, parent_node: BetModelConfigurationNode, child_node: BetModelConfigurationNode):
        exploration_value = np.sqrt(2 * np.log(parent_node.n_visits) / child_node.n_visits)
        return child_node.max_score + self.__exploration_factor * exploration_value
