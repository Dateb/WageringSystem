from typing import List

from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.PastRacesContainer import PastRacesContainer
from DataCollection.RaceCardFactory import RaceCardFactory
from DataCollection.Scraper import get_scraper
from DataAbstraction.RaceCard import RaceCard


class RaceCardsCollector:

    def __init__(self, initial_race_cards: List[RaceCard], initial_past_races_container: PastRacesContainer):
        self.__race_cards = initial_race_cards
        self.__past_races_container = initial_past_races_container

        self.__raw_race_card_factory = RaceCardFactory()
        self.__formguide_factory = FormGuideFactory()
        self.__scraper = get_scraper()

    def collect_from_race_ids(self, race_ids: List[str]) -> List[RaceCard]:
        counter = 0
        n_race_cards = len(race_ids)
        new_raw_race_cards = []
        for race_id in race_ids:
            print(f"Race card: {counter}/{n_race_cards}...")
            raw_race_card = self.__raw_race_card_factory.run(race_id)
            new_raw_race_cards.append(raw_race_card)
            self.__past_races_container.load_past_races(raw_race_card)
            counter += 1

        self.__race_cards += new_raw_race_cards
        return new_raw_race_cards

    @property
    def race_cards(self) -> List[RaceCard]:
        return self.__race_cards

    @property
    def past_races(self) -> dict:
        return self.__past_races_container.raw_past_races
