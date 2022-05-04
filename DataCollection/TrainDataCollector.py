from datetime import date, timedelta
from typing import Set

from DataCollection.RawRaceCardsCollector import RawRaceCardsCollector
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence


class TrainDataCollector:

    __TIME_OF_A_DAY = timedelta(days=1)

    def __init__(self):
        self.__raw_race_cards_persistence = RawRaceCardsPersistence(file_name="train_raw_race_cards")
        self.__past_races_container_persistence = PastRacesContainerPersistence(file_name="train_past_races")

        initial_raw_race_cards = self.__raw_race_cards_persistence.load()
        initial_past_races_container = self.__past_races_container_persistence.load()

        self.__raw_race_cards_collector = RawRaceCardsCollector(initial_raw_race_cards, initial_past_races_container)

    def collect(self, query_date: date):
        newest_train_date = self.__raw_race_cards_collector.latest_date

        if newest_train_date > query_date:
            self.__raw_race_cards_collector.collect_from_date_interval(query_date, newest_train_date)

        self.__raw_race_cards_persistence.save(self.__raw_race_cards_collector.raw_race_cards)
        self.__past_races_container_persistence.save(self.__raw_race_cards_collector.raw_past_races)

