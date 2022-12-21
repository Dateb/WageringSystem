from typing import List, Any, Dict

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
        self.feature_manager = feature_manager
        self.__model_evaluator = model_evaluator
        self.current_day = None
        self.current_day_race_cards = []

    def race_cards_to_array(self, sample_race_cards: Dict[str, RaceCard]) -> ndarray:
        self.__model_evaluator.add_results_from_race_cards(sample_race_cards)
        sample_values = []
        for datetime in sorted(sample_race_cards):
            next_race_card = sample_race_cards[datetime]
            if next_race_card.date != self.current_day:
                for race_card in self.current_day_race_cards:
                    self.feature_manager.set_features([race_card])
                    race_card.set_horse_relevance()
                    horse_values_of_race_card = self.get_values_of_race_card(race_card)
                    sample_values += horse_values_of_race_card

                self.feature_manager.post_update_feature_sources(self.current_day_race_cards)
                self.current_day = next_race_card.date
                self.current_day_race_cards = []

            self.feature_manager.pre_update_feature_sources(next_race_card)
            self.current_day_race_cards.append(next_race_card)

        return np.array(sample_values)

    def race_card_to_array(self, race_card: RaceCard) -> ndarray:
        race_card_arr = np.array(self.get_values_of_race_card(race_card))
        return race_card_arr

    def get_values_of_race_card(self, race_card: RaceCard) -> List[List[Any]]:
        horse_values_of_race_card = []
        for horse in race_card.horses:
            horse_values_of_race_card.append(race_card.values + horse.values)

        return horse_values_of_race_card
