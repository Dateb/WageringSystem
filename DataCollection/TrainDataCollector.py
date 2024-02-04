import os
import pickle
from datetime import date, timedelta
from typing import Set

from tqdm import tqdm

from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.full import FullRaceCardsCollector
from ModelTuning import simulate_conf
from Persistence.RaceCardPersistence import RaceCardsPersistence


class CollectedDaysTracker:

    def __init__(self, race_cards_persistence: RaceCardsPersistence, collected_days_file_name="../data/collected_days.pickle"):
        self.collected_days_file_name = collected_days_file_name
        self.race_cards_persistence = race_cards_persistence
        self.collected_days = []

        self.collected_days = self.get_collected_days_from_file()

    def save_collected_days_from_race_cards(self) -> None:
        print("Update collected races info based on loaded race cards...")
        self.collected_days = self.get_collected_days_from_race_cards()

        self.save_collected_days()

    def save_collected_days(self) -> None:
        with open(self.collected_days_file_name, 'wb') as handle:
            pickle.dump(self.collected_days, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def get_collected_days_from_file(self) -> Set:
        if not os.path.isfile(self.collected_days_file_name):
            return set()
        else:
            with open(self.collected_days_file_name, 'rb') as handle:
                return pickle.load(handle)

    def get_collected_days_from_race_cards(self) -> Set:
        collected_days = set()

        for race_card_file_name in tqdm(self.race_cards_persistence.race_card_file_names):
            race_cards = self.race_cards_persistence.load_race_card_files_non_writable([race_card_file_name])
            for race_card in race_cards.values():
                collected_days.add(race_card.date)

        return collected_days


class TrainDataCollector:

    __TIME_OF_A_DAY = timedelta(days=1)

    def __init__(self, race_cards_persistence: RaceCardsPersistence):
        self.race_cards_persistence = race_cards_persistence
        self.collected_days_tracker = CollectedDaysTracker(self.race_cards_persistence)

        self.collected_days_tracker.save_collected_days_from_race_cards()

        self.race_cards_collector = FullRaceCardsCollector()
        self.day_collector = DayCollector()

    def collect(self, query_date: date):
        newest_train_date = query_date
        if len(self.collected_days_tracker.collected_days) > 0:
            newest_train_date = max(self.collected_days_tracker.collected_days)

        if newest_train_date > query_date:
            self.collect_forward_until_newest_date(query_date, newest_train_date)

        self.__collect_backwards_from_query_date(query_date)

    def collect_forward_until_newest_date(self, query_date: date, newest_date: date):
        print(f"Forward collecting to date: {newest_date}")
        scraping_date = query_date
        while scraping_date != newest_date:
            if scraping_date not in self.collected_days_tracker.collected_days:
                self.collect_day(scraping_date)
            scraping_date += self.__TIME_OF_A_DAY

    def __collect_backwards_from_query_date(self, query_date: date):
        print(f"Backward collecting from date: {query_date}")
        scraping_date = query_date
        while True:
            if scraping_date not in self.collected_days_tracker.collected_days:
                self.collect_day(scraping_date)
            scraping_date -= self.__TIME_OF_A_DAY

    def collect_day(self, race_date: date):
        print(f"Currently collecting:{race_date}")
        race_ids = self.day_collector.get_closed_race_ids_of_day(race_date)
        new_race_cards = self.race_cards_collector.collect_race_cards_from_race_ids(race_ids)
        self.collected_days_tracker.collected_days.add(race_date)

        self.collected_days_tracker.save_collected_days()

        if len(race_ids) > 0:
            self.race_cards_persistence.save(new_race_cards)


def main():
    train_data_collector = TrainDataCollector(RaceCardsPersistence(simulate_conf.DEV_RACE_CARDS_FOLDER_NAME))

    day_before_yesterday = date.today() - timedelta(days=2)

    # query_date = date(
    #     year=2023,
    #     month=9,
    #     day=30,
    # )

    train_data_collector.collect(day_before_yesterday)
    #train_data_collector.collect_day(query_date)


if __name__ == '__main__':
    main()


