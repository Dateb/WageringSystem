import threading
from typing import Dict, List

import numpy as np
from pandas import DataFrame
from tqdm import trange

from DataAbstraction.Present.RaceCard import RaceCard
from Model.BetModel import BetModel
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTree import BetModelConfigurationTree
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator


class SimulateThread(threading.Thread):
    def __init__(
            self,
            samples: DataFrame,
            race_cards: Dict[str, RaceCard],
            sample_split_generator: SampleSplitGenerator,
            bet_model_configuration: BetModelConfiguration,
            validation_fold_idx: int,
            scores: List[float],
    ):
        threading.Thread.__init__(self)
        self.samples = samples
        self.race_cards = race_cards
        self.race_cards_splitter = sample_split_generator
        self.bet_model_configuration = bet_model_configuration
        self.validation_fold_idx = validation_fold_idx
        self.scores = scores

    def run(self):
        train_samples, validation_samples = self.race_cards_splitter.get_train_validation_split(self.validation_fold_idx)
        validation_race_times = list(validation_samples["date_time"].astype(str).values)

        bet_model = self.bet_model_configuration.create_bet_model()
        bet_model.fit_estimator(train_samples, validation_samples)

        validation_race_cards = {
            validation_race_time: self.race_cards[validation_race_time] for validation_race_time in validation_race_times
        }
        fund_history = bet_model.fund_history_summary(
            validation_race_cards,
            validation_samples,
            "RankerConfigurationTuner"
        )

        self.scores.append(fund_history.validation_score)


class BetModelConfigurationTuner:

    def __init__(
            self,
            race_cards: Dict[str, RaceCard],
            samples: DataFrame,
            feature_manager: FeatureManager,
            sample_split_generator: SampleSplitGenerator,
    ):
        self.race_cards = race_cards
        self.samples = samples
        self.feature_manager = feature_manager

        self.sample_split_generator = sample_split_generator

        self.__best_model: BetModel = None
        self.__init_model_configuration_setting()
        self.__max_score = -np.Inf
        self.__exploration_factor = 0.1
        self.__tree = BetModelConfigurationTree()

    def __init_model_configuration_setting(self):
        BetModelConfiguration.expected_value_additional_threshold_values = list(np.arange(0.1, 0.2, 0.02))
        BetModelConfiguration.num_leaves_values = list(np.arange(6, 18, 2))
        BetModelConfiguration.min_child_samples_values = list(np.arange(300, 550, 50))
        BetModelConfiguration.colsample_by_tree_values = list(np.arange(0.2, 1.2, 0.2))

        BetModelConfiguration.base_features = [CurrentOddsExtractor()]
        BetModelConfiguration.past_form_features = self.feature_manager.past_form_features
        BetModelConfiguration.non_past_form_features = [
            feature for feature in self.feature_manager.non_past_form_features
            if feature.get_name() != CurrentOddsExtractor().get_name()
        ]
        BetModelConfiguration.n_feature_decisions = len(BetModelConfiguration.past_form_features) + len(BetModelConfiguration.non_past_form_features)

        BetModelConfiguration.max_past_form_depth = 10
        BetModelConfiguration.n_decision_list = \
            [
                len(BetModelConfiguration.expected_value_additional_threshold_values),
                len(BetModelConfiguration.num_leaves_values),
                len(BetModelConfiguration.min_child_samples_values),
                len(BetModelConfiguration.colsample_by_tree_values),
                BetModelConfiguration.max_past_form_depth
            ] + [2 for _ in range(BetModelConfiguration.n_feature_decisions)]

    def search_for_best_configuration(self, max_iter_without_improvement: int) -> BetModel:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        self.__best_model.fit_estimator(self.samples, None)

        return self.__best_model

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()

            full_decision_list = front_node.ranker_config.get_full_decision_list()
            terminal_ranker_config = BetModelConfiguration(full_decision_list)

            score = self.__simulate(terminal_ranker_config)
            self.__backup(front_node, score)

            if score > self.__max_score:
                self.__best_model = terminal_ranker_config.create_bet_model()
                print(f"Score: {score}, Setup: {self.__best_model}")
                self.__max_score = score
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

    def __simulate(self, bet_model_configuration: BetModelConfiguration) -> float:
        scores = []
        simulation_threads = [
            SimulateThread(self.samples, self.race_cards, self.sample_split_generator, bet_model_configuration, validation_fold_idx, scores)
            for validation_fold_idx in range(len(self.sample_split_generator.validation_folds))
        ]
        for simulation_thread in simulation_threads:
            simulation_thread.start()

        for simulation_thread in simulation_threads:
            simulation_thread.join()

        return sum(scores)

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
