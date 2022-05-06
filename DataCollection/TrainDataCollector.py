from datetime import date, timedelta
from typing import Set

from DataCollection.DayCollector import DayCollector
from DataCollection.RaceCardsCollector import RaceCardsCollector
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RaceCardPersistence import RaceCardsPersistence


class TrainDataCollector:

    __TIME_OF_A_DAY = timedelta(days=1)

    def __init__(self):
        self.__raw_race_cards_persistence = RaceCardsPersistence(file_name="train_race_cards")
        self.__past_races_container_persistence = PastRacesContainerPersistence(file_name="train_past_races")

        initial_raw_race_cards = self.__raw_race_cards_persistence.load()
        initial_past_races_container = self.__past_races_container_persistence.load()

        self.__race_cards_collector = RaceCardsCollector(initial_raw_race_cards, initial_past_races_container)
        self.__day_collector = DayCollector()
        self.__collected_days = self.__get_collected_days()

    def collect(self, query_date: date):
        newest_train_date = self.latest_date

        if newest_train_date > query_date:
            self.__collect_forward_until_newest_train_date(query_date, newest_train_date)

        self.__collect_backwards_from_query_date(query_date)

    def __collect_forward_until_newest_train_date(self, query_date: date, newest_train_date: date):
        print(f"Forward collecting to date: {newest_train_date}")
        scraping_date = query_date
        while scraping_date != newest_train_date:
            if scraping_date not in self.__collected_days:
                self.__collect_day(scraping_date)
            scraping_date += self.__TIME_OF_A_DAY

    def __collect_backwards_from_query_date(self, query_date):
        print(f"Backward collecting from date: {query_date}")
        scraping_date = query_date
        while True:
            if scraping_date not in self.__collected_days:
                self.__collect_day(scraping_date)
            scraping_date -= self.__TIME_OF_A_DAY

    def __collect_day(self, day):
        print(f"Currently collecting:{day}")
        race_ids = self.__day_collector.get_closed_race_ids_of_day(day)
        self.__race_cards_collector.collect_from_race_ids(race_ids)
        self.__collected_days.add(day)

        self.__raw_race_cards_persistence.save(self.__race_cards_collector.race_cards)
        self.__past_races_container_persistence.save(self.__race_cards_collector.past_races)

    def __get_collected_days(self) -> Set[date]:
        return {race_card.date for race_card in self.__race_cards_collector.race_cards}

    @property
    def latest_date(self) -> date:
        return max(self.__collected_days)


def main():
    train_data_collector = TrainDataCollector()

    query_date = date(2022, 5, 6)

    train_data_collector.collect(query_date)


if __name__ == '__main__':
    main()


