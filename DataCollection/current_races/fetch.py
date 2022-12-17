from datetime import datetime
from typing import List

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class TodayRaceCardsFetcher:

    def __init__(self):
        self.today = datetime.today().date()

    def fetch_today_race_cards(self) -> List[WritableRaceCard]:
        race_ids_today = DayCollector().get_open_race_ids_of_day(self.today)
        today_race_cards = BaseRaceCardsCollector().collect_race_cards_from_race_ids(race_ids_today)
        today_race_cards.sort(key=lambda x: x.datetime)

        return today_race_cards
