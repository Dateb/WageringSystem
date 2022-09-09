import threading
from typing import Dict

import numpy as np
from numpy import ndarray

from ModelTuning.ModelEvaluator import ModelEvaluator
from Persistence import RaceCardPersistence
from SampleExtraction.FeatureManager import FeatureManager


class SampleExtractionThread(threading.Thread):
    def __init__(
            self,
            race_cards_loader: RaceCardPersistence,
            feature_manager: FeatureManager,
            race_cards_file_name: str,
            race_arr_per_month: Dict[str, ndarray],
            model_evaluator: ModelEvaluator,
    ):
        threading.Thread.__init__(self)
        self.__race_cards_loader = race_cards_loader
        self.__feature_manager = feature_manager
        self.__race_cards_file_name = race_cards_file_name
        self.__race_arr_per_month = race_arr_per_month
        self.__model_evaluator = model_evaluator

    def run(self):
        sample_race_cards = self.__race_cards_loader.load_race_card_files_non_writable([self.__race_cards_file_name])

        self.__model_evaluator.add_results_from_race_cards(sample_race_cards)

        sample_race_cards = list(sample_race_cards.values())
        self.__feature_manager.set_features(sample_race_cards)

        horse_values = []
        for race_card in sample_race_cards:
            for horse in race_card.horses:
                horse_values.append(race_card.values + horse.values)

        self.__race_arr_per_month[self.__race_cards_file_name] = np.array(horse_values)
