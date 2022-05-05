from datetime import date, timedelta
from typing import List, Set

from DataCollection.DayCollector import DayCollector
from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.PastRacesContainer import PastRacesContainer
from DataCollection.RawRaceCard import RawRaceCard
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from DataCollection.Scraper import get_scraper
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence
from SampleExtraction.RaceCard import RaceCard


class RawRaceCardsCollector:

    def __init__(self, initial_raw_race_cards: List[RawRaceCard], initial_past_races_container: PastRacesContainer):
        self.__raw_race_cards = initial_raw_race_cards
        self.__past_races_container = initial_past_races_container

        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__formguide_factory = FormGuideFactory()
        self.__scraper = get_scraper()

    def collect_from_date_interval(self, start_date: date, end_date: date):
        self.__scraper.start()

        time_of_a_day = timedelta(days=1)
        current_date = start_date
        while current_date != end_date:
            print(f"Currently at day:{current_date} (end: {end_date})...")
            self.collect_from_day(current_date)
            current_date += time_of_a_day

        self.__scraper.stop()

    def collect_from_race_ids(self, race_ids: List[str]) -> List[RawRaceCard]:
        counter = 0
        n_race_cards = len(race_ids)
        new_raw_race_cards = []
        for race_id in race_ids:
            print(f"Race card: {counter}/{n_race_cards}...")
            raw_race_card = self.__raw_race_card_factory.run(race_id)
            new_raw_race_cards.append(raw_race_card)
            self.__past_races_container.load_past_races(raw_race_card)
            counter += 1

        self.__raw_race_cards += new_raw_race_cards
        return new_raw_race_cards

    @property
    def raw_race_cards(self):
        return self.__raw_race_cards

    @property
    def race_cards(self):
        return [RaceCard(raw_race_card) for raw_race_card in self.__raw_race_cards]

    @property
    def raw_past_races(self) -> dict:
        return self.__past_races_container.raw_past_races


def main():
    raw_race_cards_persistence = RawRaceCardsPersistence(file_name="train_raw_race_cards")
    past_races_container_persistence = PastRacesContainerPersistence(file_name="train_past_races")

    start_date = date(2022, 4, 1)
    end_date = date(2022, 4, 25)

    time_of_a_day = timedelta(days=1)
    current_date = start_date
    while current_date != end_date:
        initial_raw_race_cards = raw_race_cards_persistence.load()
        initial_past_races_container = past_races_container_persistence.load()

        raw_race_cards_collector = RawRaceCardsCollector(initial_raw_race_cards, initial_past_races_container)
        raw_race_cards_collector.collect_from_day(current_date)

        print(len(raw_race_cards_collector.raw_race_cards))

        raw_race_cards_persistence.save(raw_race_cards_collector.raw_race_cards)
        past_races_container_persistence.save(raw_race_cards_collector.raw_past_races)

        current_date += time_of_a_day


if __name__ == '__main__':
    main()
