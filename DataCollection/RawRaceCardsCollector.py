from datetime import date
from random import randrange
from typing import List

from DataCollection.DayCollector import DayCollector
from DataCollection.FormGuide import FormGuide
from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.PastRacesContainer import PastRacesContainer
from DataCollection.RaceHistory import RaceHistory
from DataCollection.RawRaceCard import RawRaceCard
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from DataCollection.Scraper import get_scraper
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence


class RawRaceCardsCollector:

    def __init__(self, initial_raw_race_cards: List[RawRaceCard], past_races_container: PastRacesContainer):
        self.__n_collected_races = 0

        self.__raw_race_cards = initial_raw_race_cards
        self.__past_races_container = past_races_container

        self.__discovered_race_ids = [raw_race_card.race_id for raw_race_card in self.__raw_race_cards]

        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__formguide_factory = FormGuideFactory()
        self.__scraper = get_scraper()
        self.__day_collector = DayCollector()

    def collect_from_day(self, day: date):
        race_ids = self.__day_collector.get_race_ids_of_day(day)
        print(len(race_ids))
        self.__collect_from_race_ids(race_ids)

    def __collect_from_race_ids(self, race_ids: List[str]):
        for race_id in race_ids:
            raw_race_card = self.__raw_race_card_factory.run(race_id)
            self.__raw_race_cards.append(raw_race_card)
            self.__past_races_container.load_past_races(raw_race_card)

    @property
    def race_ids(self):
        return self.__discovered_race_ids

    @property
    def raw_race_cards(self):
        return self.__raw_race_cards

    @property
    def raw_past_races(self) -> dict:
        return self.__past_races_container.raw_past_races


def main():
    race_card_persistence = RawRaceCardsPersistence(file_name="test_raw_race_cards")
    past_race_container_persistence = PastRacesContainerPersistence(file_name="test_past_races")
    initial_raw_race_cards = race_card_persistence.load()
    past_race_container = past_race_container_persistence.load()

    raw_race_cards_collector = RawRaceCardsCollector(initial_raw_race_cards, past_race_container)

    day_of_race = date(2022, 5, 1)
    raw_race_cards_collector.collect_from_day(day_of_race)

    print(len(raw_race_cards_collector.raw_race_cards))
    race_card_persistence.save(raw_race_cards_collector.raw_race_cards)
    past_race_container_persistence.save(raw_race_cards_collector.raw_past_races)


if __name__ == '__main__':
    main()
