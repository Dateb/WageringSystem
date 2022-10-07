from typing import List, Any

import numpy as np
from numpy import ndarray

from DataAbstraction.Present.RaceCard import RaceCard
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

    def race_card_file_to_array(self, race_cards_file_name: str) -> ndarray:
        sample_race_cards = self.__race_cards_loader.load_race_card_files_non_writable([race_cards_file_name])

        self.__model_evaluator.add_results_from_race_cards(sample_race_cards)
        sample_values = []
        for datetime in sorted(sample_race_cards):
            horse_values_of_race_card = self.get_values_of_race_card(sample_race_cards[datetime])
            sample_values += horse_values_of_race_card

        return np.array(sample_values)

    def race_card_to_array(self, race_card: RaceCard) -> ndarray:
        return np.array(self.get_values_of_race_card(race_card))

    def get_values_of_race_card(self, race_card: RaceCard) -> List[List[Any]]:
        self.__feature_manager.set_features([race_card])

        horse_values_of_race_card = []
        for horse in race_card.horses:
            horse_values_of_race_card.append(race_card.values + horse.values)

        return horse_values_of_race_card
