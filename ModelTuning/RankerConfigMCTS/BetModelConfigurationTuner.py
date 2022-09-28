import threading
from statistics import mean

import numpy as np
from tqdm import trange

from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTree import BetModelConfigurationTree
from SampleExtraction.Extractors.current_race_based import CurrentOdds
from SampleExtraction.Extractors.time_based import MonthCosExtractor, MonthSinExtractor, WeekDayCosExtractor, \
    WeekDaySinExtractor, HourCosExtractor, HourSinExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator


class SimulateThread(threading.Thread):
    def __init__(
            self,
            race_cards_sample: RaceCardsSample,
            sample_split_generator: SampleSplitGenerator,
            model_evaluator: ModelEvaluator,
            bet_model_configuration: BetModelConfiguration,
            validation_fold_idx: int,
            results: dict,
    ):
        threading.Thread.__init__(self)
        self.race_cards_sample = race_cards_sample
        self.race_cards_splitter = sample_split_generator
        self.model_evaluator = model_evaluator
        self.bet_model_configuration = bet_model_configuration
        self.validation_fold_idx = validation_fold_idx
        self.scores = results

    def run(self):
        train_samples, validation_samples = self.race_cards_splitter.get_train_validation_split(self.validation_fold_idx)

        bet_model = self.bet_model_configuration.create_bet_model()
        bet_model.fit_estimator(train_samples.race_cards_dataframe, validation_samples.race_cards_dataframe)

        fund_history_summary = self.model_evaluator.get_fund_history_summary_of_model(bet_model, validation_samples)

        self.scores[self.validation_fold_idx] = fund_history_summary.validation_score


class BetModelConfigurationTuner:

    def __init__(
            self,
            race_cards_sample: RaceCardsSample,
            feature_manager: FeatureManager,
            sample_split_generator: SampleSplitGenerator,
            model_evaluator: ModelEvaluator,
    ):
        self.race_cards_sample = race_cards_sample
        self.feature_manager = feature_manager

        self.sample_split_generator = sample_split_generator
        self.model_evaluator = model_evaluator

        self.__best_configuration: BetModelConfiguration = None
        self.__init_model_configuration_setting()
        self.__max_score = -np.Inf
        self.__exploration_factor = 0.1
        self.__tree = BetModelConfigurationTree()

    def __init_model_configuration_setting(self):
        BetModelConfiguration.expected_value_additional_threshold_values = [0.0]
        BetModelConfiguration.num_leaves_values = [3]
        BetModelConfiguration.min_child_samples_values = list(np.arange(500, 550, 50))

        BetModelConfiguration.base_features = [
            CurrentOdds(),
            MonthCosExtractor(), MonthSinExtractor(),
            WeekDayCosExtractor(), WeekDaySinExtractor(),
            HourCosExtractor(), HourSinExtractor(),
        ]

        base_feature_names = [feature.get_name() for feature in BetModelConfiguration.base_features]
        BetModelConfiguration.non_past_form_features = [
            feature for feature in self.feature_manager.non_past_form_features
            if feature.get_name() not in base_feature_names
        ]
        BetModelConfiguration.n_feature_decisions = len(BetModelConfiguration.non_past_form_features)

        BetModelConfiguration.n_decision_list = \
            [
                len(BetModelConfiguration.expected_value_additional_threshold_values),
                len(BetModelConfiguration.num_leaves_values),
                len(BetModelConfiguration.min_child_samples_values),
            ] + [2 for _ in range(BetModelConfiguration.n_feature_decisions)]

    def search_for_best_configuration(self, max_iter_without_improvement: int) -> BetModelConfiguration:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        return self.__best_configuration

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()

            full_decision_list = front_node.ranker_config.get_full_decision_list()
            terminal_configuration = BetModelConfiguration(full_decision_list)

            results = self.__simulate(terminal_configuration)
            score = mean(list(results.values()))
            self.__backup(front_node, score)

            if score > self.__max_score:
                self.__best_configuration = terminal_configuration
                print("New best Result:")
                for month_year in results:
                    print(f"{month_year}: {results[month_year]}")
                print(f"Score: {score}")
                print("----------------------------------------")
                print(f"Setup: {self.__best_configuration}")
                print("----------------------------------------")
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

    def __simulate(self, bet_model_configuration: BetModelConfiguration) -> dict:
        results = {}
        simulation_threads = [
            SimulateThread(self.race_cards_sample, self.sample_split_generator, self.model_evaluator, bet_model_configuration, validation_fold_idx, results)
            for validation_fold_idx in range(self.sample_split_generator.n_folds)
        ]
        for simulation_thread in simulation_threads:
            simulation_thread.start()

        for simulation_thread in simulation_threads:
            simulation_thread.join()

        return results

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
