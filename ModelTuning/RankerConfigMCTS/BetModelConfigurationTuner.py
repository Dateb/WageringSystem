import threading
from statistics import mean, stdev

import numpy as np
from tqdm import trange

from Model.Probabilizing.Probabilizer import Probabilizer
from ModelTuning.FeatureScorer import FeatureScorer
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTree import BetModelConfigurationTree
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.BlockSplitter import BlockSplitter
from util.stats_calculator import ExponentialOnlineCalculator


class SimulateThread(threading.Thread):
    def __init__(
            self,
            sample_splitter: BlockSplitter,
            validation_block_idx: int,
            model_evaluator: ModelEvaluator,
            bet_model_configuration: BetModelConfiguration,
            results: dict,
    ):
        threading.Thread.__init__(self)
        self.sample_splitter = sample_splitter
        self.validation_block_idx = validation_block_idx
        self.model_evaluator = model_evaluator
        self.bet_model_configuration = bet_model_configuration
        self.scores = results

    def run(self):
        train_sample, validation_sample, _ = self.sample_splitter.get_block_split(self.validation_block_idx)

        bet_model = self.bet_model_configuration.create_bet_model(train_sample)

        fund_history_summary = self.model_evaluator.get_fund_history_summary_of_model(bet_model, validation_sample)

        self.scores[self.validation_block_idx] = fund_history_summary.score


class BetModelConfigurationTuner:

    def __init__(
            self,
            race_cards_sample: RaceCardsSample,
            feature_manager: FeatureManager,
            sample_splitter: BlockSplitter,
            model_evaluator: ModelEvaluator,
    ):
        self.race_cards_sample = race_cards_sample
        self.feature_manager = feature_manager

        self.sample_splitter = sample_splitter
        self.model_evaluator = model_evaluator

        self.__best_configuration: BetModelConfiguration = None
        self.__max_score = -np.Inf
        self.__exploration_factor = 0.1

        root_node = BetModelConfigurationNode(
            identifier="root",
            max_score=-np.Inf,
            n_visits=0,
            ranker_config=BetModelConfiguration(
                decisions=[],
                base_features=self.feature_manager.base_features,
                search_features=self.feature_manager.search_features,
            ),
        )

        self.tree = BetModelConfigurationTree(root_node)
        self.feature_scorer = FeatureScorer(self.feature_manager.search_features, report_interval=50)

    def search_for_best_configuration(self, max_iter_without_improvement: int) -> BetModelConfiguration:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        return self.__best_configuration

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()

            full_decision_list = front_node.ranker_config.get_full_decision_list()
            terminal_configuration = BetModelConfiguration(
                full_decision_list,
                self.feature_manager.base_features,
                self.feature_manager.search_features,
            )

            results = self.__simulate(terminal_configuration)

            payout_mean = mean(list(results.values()))
            total_score = payout_mean

            train_sample, test_sample = self.sample_splitter.get_train_test_split()

            bet_model = terminal_configuration.create_bet_model(train_sample)
            test_score = self.model_evaluator.get_fund_history_summary_of_model(bet_model, test_sample).score

            print(f"Score: {total_score} (Test score: {test_score})")

            self.__backup(front_node, total_score)

            self.feature_scorer.update_feature_scores(total_score, terminal_configuration.selected_search_features)

            if total_score > self.__max_score:
                self.__best_configuration = terminal_configuration
                print("New best Result:")
                for month_year in results:
                    print(f"{month_year}: {results[month_year]}")
                print(terminal_configuration)

                self.__max_score = total_score

                return True

        return False

    def __select(self):
        node = self.tree.node("root")
        while not node.ranker_config.is_terminal:
            if not self.__is_node_fully_expanded(node):
                return self.__expand(node)
            else:
                node = self.__select_best_children(node)

        return node

    def __expand(self, node: BetModelConfigurationNode):
        next_action_idx = len(self.tree.children(node.identifier))
        decisions_children = node.ranker_config.decisions + [next_action_idx]
        children_ranker_config = BetModelConfiguration(
            decisions_children,
            self.feature_manager.base_features,
            self.feature_manager.search_features,
        )

        new_node = BetModelConfigurationNode(
            identifier=children_ranker_config.identifier,
            max_score=0,
            n_visits=0,
            ranker_config=children_ranker_config,
        )
        return self.tree.add_node(new_node, node)

    def __simulate(self, bet_model_configuration: BetModelConfiguration) -> dict:
        results = {}
        simulation_threads = [SimulateThread(
            self.sample_splitter,
            validation_block_idx,
            self.model_evaluator,
            bet_model_configuration,
            results
        ) for validation_block_idx in range(self.sample_splitter.block_count - 1)]

        for simulation_thread in simulation_threads:
            simulation_thread.start()
            simulation_thread.join()

        return results

    def __backup(self, front_node: BetModelConfigurationNode, score: float):
        node = front_node
        while node.identifier != "root":
            node.n_visits += 1
            if score > node.max_score:
                node.max_score = score
            node = self.tree.parent(node.identifier)
        node.n_visits += 1

    def __is_node_fully_expanded(self, node):
        return len(self.tree.children(node.identifier)) == node.ranker_config.n_decisions_next_action

    def __select_best_children(self, node: BetModelConfigurationNode):
        children = self.tree.children(node.identifier)

        children_uct = np.array([self.__get_uct(node, child) for child in children])
        return children[children_uct.argmax()]

    def __get_uct(self, parent_node: BetModelConfigurationNode, child_node: BetModelConfigurationNode):
        exploration_value = np.sqrt(2 * np.log(parent_node.n_visits) / child_node.n_visits)
        return child_node.max_score + self.__exploration_factor * exploration_value
