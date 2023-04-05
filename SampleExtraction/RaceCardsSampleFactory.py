from typing import List, Any, Dict

import numpy as np
from numpy import ndarray
from tqdm import tqdm

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.ModelEvaluator import ModelEvaluator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder


class RaceCardsSampleFactory:
    def __init__(
            self,
            feature_manager: FeatureManager,
            model_evaluator: ModelEvaluator,
            n_warm_up_months: int = 1,
            n_sample_months: int = 1,
    ):
        n_total_months = n_warm_up_months + n_sample_months
        self.race_cards_loader = RaceCardsPersistence("race_cards")
        self.warm_up_race_card_file_names = self.race_cards_loader.race_card_file_names[-n_total_months:-n_sample_months]
        self.sample_race_card_file_names = self.race_cards_loader.race_card_file_names[-n_sample_months:]

        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator

        self.current_day = None
        self.current_day_race_cards = []

        # features not known from the container race card
        # TODO: this throws an indexerror when containers are none
        container_race_cards = self.race_cards_loader.load_race_card_files_non_writable(self.warm_up_race_card_file_names)
        container_race_cards = list(container_race_cards.values())
        columns = container_race_cards[0].attributes + feature_manager.feature_names

        self.sample_encoder = SampleEncoder(feature_manager.features, columns)

    def warm_up(self) -> None:
        for race_card_file_name in tqdm(self.warm_up_race_card_file_names):
            race_cards = self.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            self.model_evaluator.add_results_from_race_cards(race_cards)

            self.race_cards_to_array(race_cards)

    def create_race_cards_sample(self) -> RaceCardsSample:
        for race_card_file_name in tqdm(self.sample_race_card_file_names):
            race_cards = self.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            self.model_evaluator.add_results_from_race_cards(race_cards)
            arr_of_race_cards = self.race_cards_to_array(race_cards)
            self.sample_encoder.add_race_cards_arr(arr_of_race_cards)

        race_cards_sample = self.sample_encoder.get_race_cards_sample()
        race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

        return race_cards_sample

    def race_cards_to_array(self, sample_race_cards: Dict[str, RaceCard]) -> ndarray:
        sample_values = []
        for datetime in sorted(sample_race_cards):
            next_race_card = sample_race_cards[datetime]
            if next_race_card.date != self.current_day:
                for race_card in self.current_day_race_cards:
                    if race_card.sample_validity:
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
        self.feature_manager.set_features([race_card])
        race_card_arr = np.array(self.get_values_of_race_card(race_card))
        return race_card_arr

    def get_values_of_race_card(self, race_card: RaceCard) -> List[List[Any]]:
        horse_values_of_race_card = []
        for horse in race_card.horses:
            horse_values_of_race_card.append(race_card.values + horse.values)

        return horse_values_of_race_card
