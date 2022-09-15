import numpy as np
from numpy import ndarray

from ModelTuning.ModelEvaluator import ModelEvaluator
from Persistence import RaceCardPersistence
from SampleExtraction.FeatureManager import FeatureManager


class RaceCardsArrayFactory:
    def __init__(
            self,
            race_cards_loader: RaceCardPersistence,
            feature_manager: FeatureManager,
            model_evaluator: ModelEvaluator,
    ):
        self.__race_cards_loader = race_cards_loader
        self.__feature_manager = feature_manager
        self.__model_evaluator = model_evaluator

    def generate_from_race_cards_file(self, race_cards_file_name: str) -> ndarray:
        sample_race_cards = self.__race_cards_loader.load_race_card_files_non_writable([race_cards_file_name])

        self.__model_evaluator.add_results_from_race_cards(sample_race_cards)

        sample_race_cards = list(sample_race_cards.values())
        self.__feature_manager.set_features(sample_race_cards)

        horse_values = []
        for race_card in sample_race_cards:
            for horse in race_card.horses:
                horse_values.append(race_card.values + horse.values)

        return np.array(horse_values)
