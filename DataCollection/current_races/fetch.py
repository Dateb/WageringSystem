from datetime import datetime, date
from typing import List

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.TrainDataCollector import TrainDataCollector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class TodayRaceCardsFetcher:

    def __init__(self):
        print("Initialising races:")

        self.today = datetime.today().date()
        self.collect_race_cards_until_today()

    def collect_race_cards_until_today(self):
        train_data_collector = TrainDataCollector(file_name="race_cards")
        query_date = date(year=2022, month=1, day=1)
        train_data_collector.collect_forward_until_newest_date(query_date=query_date, newest_date=self.today)

    def fetch_today_race_cards(self) -> List[WritableRaceCard]:
        race_ids_today = DayCollector().get_open_race_ids_of_day(self.today)
        today_race_cards = BaseRaceCardsCollector().collect_race_cards_from_race_ids(race_ids_today)
        today_race_cards.sort(key=lambda x: x.datetime)

        return today_race_cards
