from typing import List

from treelib import Tree

from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.SampleSet import SampleSet
from Experiments.Validator import Validator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder


class FeatureSelector:

    def __init__(self, max_rounds: int = 100):
        raw_races = RaceCardsPersistence("train_race_cards").load_raw()
        race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]

        sample_encoder = SampleEncoder(FeatureManager())
        samples = sample_encoder.transform(race_cards)
        sample_set = SampleSet(samples)
        bettor = WinBettor(kelly_wealth=1000)

        self.__max_rounds = max_rounds
        self.__validator = Validator(bettor, sample_set, raw_races)

        self.__root_features = [CurrentOddsExtractor().get_name()]
        self.__tree = Tree()
        self.__root_id = str(self.__root_features)
        self.__tree.create_node(identifier=self.__root_id, data={"features": self.__root_features})
        self.__remaining_node_ids = [self.__root_id]
        self.__best_node_id = self.__root_id

    def run(self):
        while self.__remaining_node_ids:
            next_node_id = self.__remaining_node_ids.pop(0)
            node = self.__tree.get_node(next_node_id)
            self.__run_node(node)

    def __run_node(self, node):
        feature_names = node.data["features"]
        node.data["performance"] = self.__get_feature_combination_performance(feature_names)
        self.__add_children_to_node(node)
        self.__update_best_node(node)

    def __get_feature_combination_performance(self, feature_names: List[str]) -> float:
        total_performance = 0
        n_rounds = 1
        while n_rounds <= self.__max_rounds:
            performance_of_round = self.__validate_feature_names_for_round(feature_names, n_rounds)
            if performance_of_round <= 1.0:
                total_performance += performance_of_round
                return total_performance

            total_performance += 1.0
            n_rounds += 1

        return total_performance

    def __validate_feature_names_for_round(self, feature_names: List[str], round_nr: int) -> float:
        estimator = BoostedTreesRanker(feature_names)
        fund_history_summary = self.__validator.create_random_fund_history(
            estimator=estimator,
            name="Feature_Selected_Ranker",
            random_state=round_nr,
        )

        win_loss_ratio = fund_history_summary.win_loss_ratio
        return win_loss_ratio

    def __add_children_to_node(self, node):
        node_id = node.identifier
        if node_id != self.__root_id:
            parent = self.__tree.parent(node.identifier)
            if parent.data["performance"] > node.data["performance"]:
                return 0
        node_features = node.data["features"]

        node_identifier = str(node_features)
        feature_candidates = [
            feature for feature in FeatureManager.FEATURE_NAMES if feature not in node_features
        ]
        for feature_candidate in feature_candidates:
            child_features = node_features + [feature_candidate]
            child_features.sort()
            child_identifier = str(child_features)
            if not self.__tree.contains(child_identifier):
                self.__tree.create_node(identifier=child_identifier, parent=node_identifier, data={"features": child_features})
                self.__remaining_node_ids = [child_identifier] + self.__remaining_node_ids

    def __update_best_node(self, new_node):
        best_node = self.__tree.get_node(self.__best_node_id)
        if new_node.data["performance"] > best_node.data["performance"]:
            best_features = new_node.data["features"]
            best_performance = new_node.data["performance"]
            print(f"Found new best features {best_features} with score: {best_performance}")
            self.__best_node_id = new_node.identifier


def main():
    #feature_selector = FeatureSelector()
    #feature_selector.run()
    FeatureManager.FEATURE_NAMES.sort()
    print(FeatureManager.FEATURE_NAMES)
    print('finished')


if __name__ == '__main__':
    main()
