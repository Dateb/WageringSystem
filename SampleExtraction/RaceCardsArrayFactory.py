from typing import List, Any, Dict

import numpy as np
from numpy import ndarray

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.ModelEvaluator import ModelEvaluator
from SampleExtraction.FeatureManager import FeatureManager


class RaceCardsArrayFactory:
    def __init__(
            self,
            feature_manager: FeatureManager,
            encode_only_runners: bool = True,
    ):
        self.feature_manager = feature_manager
        self.encode_runners = encode_only_runners

    def race_cards_to_array(self, sample_race_cards: Dict[str, RaceCard]) -> ndarray:
        first_key = sorted(sample_race_cards.keys())[0]
        current_day = sample_race_cards[first_key].date
        current_day_race_cards = []
        sample_values = []
        for datetime in sorted(sample_race_cards):
            next_race_card = sample_race_cards[datetime]
            if next_race_card.date != current_day:
                # print(f"{next_race_card.date} != {current_day}")
                sample_values = self.process_current_day_race_cards(current_day_race_cards, sample_values)
                current_day = next_race_card.date
                current_day_race_cards = []

            self.feature_manager.pre_update_feature_sources(next_race_card)
            current_day_race_cards.append(next_race_card)

        sample_values = self.process_current_day_race_cards(current_day_race_cards, sample_values)

        return np.array(sample_values)

    def process_current_day_race_cards(self, current_day_race_cards: List[RaceCard], sample_values: List) -> List:
        for race_card in current_day_race_cards:
            race_card.set_momentum_of_runners()
            if race_card.is_valid_sample:
                self.feature_manager.set_features([race_card])
                horse_values_of_race_card = self.get_values_of_race_card(race_card)
                sample_values += horse_values_of_race_card

        self.feature_manager.post_update_feature_sources(current_day_race_cards)
        return sample_values

    def race_card_to_array(self, race_card: RaceCard) -> ndarray:
        self.feature_manager.set_features([race_card])
        race_card_arr = np.array(self.get_values_of_race_card(race_card))
        return race_card_arr

    def get_values_of_race_card(self, race_card: RaceCard) -> List[List[Any]]:
        horse_values_of_race_card = []
        if self.encode_runners:
            for horse in race_card.runners:
                horse_values_of_race_card.append(race_card.values + horse.values)

        else:
            for horse in race_card.horses:
                horse_values_of_race_card.append(race_card.values + horse.values)

        return horse_values_of_race_card
