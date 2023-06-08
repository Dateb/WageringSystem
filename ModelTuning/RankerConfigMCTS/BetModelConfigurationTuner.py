import numpy as np
from tqdm import trange

from ModelTuning.FeatureScorer import FeatureScorer
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.EstimatorConfiguration import EstimatorConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationNode import BetModelConfigurationNode
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTree import BetModelConfigurationTree
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.BlockSplitter import BlockSplitter


class BetModelConfigurationTuner:

    def __init__(
            self,
            train_sample: RaceCardsSample,
            feature_manager: FeatureManager,
            sample_splitter: BlockSplitter,
            model_evaluator: ModelEvaluator,
    ):
        self.train_sample = train_sample
        self.feature_manager = feature_manager

        self.sample_splitter = sample_splitter
        self.model_evaluator = model_evaluator

        self.__best_configuration: EstimatorConfiguration = None
        self.__max_score = -np.Inf
        self.__exploration_factor = 0.1

        root_node = BetModelConfigurationNode(
            identifier="root",
            max_score=-np.Inf,
            n_visits=0,
            ranker_config=EstimatorConfiguration(
                decisions=[],
                base_features=self.feature_manager.base_features,
                search_features=self.feature_manager.search_features,
            ),
        )

        self.tree = BetModelConfigurationTree(root_node)
        self.feature_scorer = FeatureScorer(self.feature_manager.search_features, report_interval=10)

    def search_for_best_configuration(self, max_iter_without_improvement: int) -> EstimatorConfiguration:
        while self.__improve_ranker_config(max_iter_without_improvement):
            pass

        return self.__best_configuration

    def __improve_ranker_config(self, max_iter_without_improvement: int) -> bool:
        for _ in trange(max_iter_without_improvement):
            front_node = self.__select()

            full_decision_list = front_node.ranker_config.get_full_decision_list()
            terminal_configuration = EstimatorConfiguration(
                full_decision_list,
                self.feature_manager.base_features,
                self.feature_manager.search_features,
            )

            total_score = self.__simulate(terminal_configuration)

            self.__backup(front_node, total_score)

            if total_score > self.__max_score:
                self.__best_configuration = terminal_configuration
                print(f"New best total score: {total_score}")
                print(f"Under this configuration: {terminal_configuration}")

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
        children_ranker_config = EstimatorConfiguration(
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

    def __simulate(self, bet_model_configuration: EstimatorConfiguration) -> float:
        sample, _ = self.sample_splitter.get_train_test_split()
        return bet_model_configuration.validate_estimator(sample)

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
