import datetime
from abc import ABC
from typing import List

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.DayCollector import DayCollector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class CurrentRaceCardsFetcher(ABC):

    def __init__(self):
        self.date = datetime.date.today()

    def fetch_race_cards(self) -> List[WritableRaceCard]:
        race_ids = DayCollector().get_open_race_ids_of_day(self.date)
        race_cards = BaseRaceCardsCollector().collect_race_cards_from_race_ids(race_ids)
        race_cards.sort(key=lambda x: x.datetime)

        return race_cards


class TodayRaceCardsFetcher(CurrentRaceCardsFetcher):

    def __init__(self):
        super().__init__()


class TomorrowRaceCardsFetcher(CurrentRaceCardsFetcher):

    def __init__(self):
        super().__init__()
        self.date = datetime.date.today() + datetime.timedelta(days=1)
