import threading
from typing import Dict
from numpy import ndarray
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory


class SampleExtractionThread(threading.Thread):
    def __init__(
        self,
        race_cards_array_factory: RaceCardsArrayFactory,
        race_cards_file_name: str,
        race_arr_per_month: Dict[str, ndarray],
    ):
        threading.Thread.__init__(self)
        self.__race_cards_array_factory = race_cards_array_factory
        self.__race_cards_file_name = race_cards_file_name
        self.__race_arr_per_month = race_arr_per_month

    def run(self):
        race_arr_of_month = self.__race_cards_array_factory.generate_from_race_cards_file(self.__race_cards_file_name)
        self.__race_arr_per_month[self.__race_cards_file_name] = race_arr_of_month
