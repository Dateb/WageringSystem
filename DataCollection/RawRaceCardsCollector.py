from random import randrange
from typing import List

from DataCollection.FormGuide import FormGuide
from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.RaceHistory import RaceHistory
from DataCollection.RawRaceCard import RawRaceCard
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from DataCollection.Scraper import get_scraper
from Persistence.RaceHistoryPersistence import RaceHistoryPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence


class RawRaceCardsCollector:

    def __init__(self, initial_raw_race_cards: List[RawRaceCard] = None, n_races=10):
        self.__n_collected_races = 0

        self.__raw_race_cards = [] if initial_raw_race_cards is None else initial_raw_race_cards
        self.__discovered_race_ids = [raw_race_card.race_id for raw_race_card in self.__raw_race_cards]

        self.__n_races = n_races

        self.__raw_race_card_factory = RawRaceCardFactory()
        self.__formguide_factory = FormGuideFactory()
        self.__scraper = get_scraper()

    def collect_from_race_histories(self, race_histories: List[RaceHistory]):
        for race_history in race_histories:
            for race_id in race_history.race_ids:
                if race_id not in self.__discovered_race_ids:
                    self.__discovered_race_ids.append(race_id)

                    raw_race_card = self.__raw_race_card_factory.run(race_id)
                    self.__raw_race_cards.append(raw_race_card)

                    self.__n_collected_races += 1

                    if self.__n_collected_races == self.__n_races:
                        self.__n_collected_races = 0
                        return 0


    def collect_by_random_navigation(self, next_race_id: str):
        print(f"race id:{next_race_id}")
        raw_race_card = self.__raw_race_card_factory.run(next_race_id)

        self.__raw_race_cards.append(raw_race_card)
        self.__n_collected_races += 1

        if self.__n_collected_races == self.__n_races:
            self.__n_collected_races = 0
            return 0

        next_race_id = self.__get_next_race_id(raw_race_card)

        self.collect_by_random_navigation(next_race_id)

    def __get_next_race_id(self, raw_race_card: RawRaceCard):
        subject_id = self.__select_subject_id(raw_race_card)
        print(f"subject id:{subject_id}")

        form_guide = self.__formguide_factory.run(subject_id)
        return self.__select_race_id(form_guide)

    def __select_subject_id(self, raw_race_card: RawRaceCard):
        subject_ids = raw_race_card.subject_ids
        random_id = randrange(len(subject_ids))
        return subject_ids[random_id]

    def __select_race_id(self, form_guide: FormGuide):
        new_race_ids = [race_id for race_id in form_guide.gb_past_race_ids
                        if race_id not in self.__discovered_race_ids]
        if not new_race_ids:
            print("Every listed race already discovered! Resorting to random race...")
            return self.__select_random_discovered_race_id()

        random_idx = randrange(len(new_race_ids))
        new_race_id = new_race_ids[random_idx]

        self.__discovered_race_ids.append(new_race_id)
        return new_race_id

    def __select_random_discovered_race_id(self):
        random_idx = randrange(len(self.__discovered_race_ids))
        return self.__discovered_race_ids[random_idx]

    @property
    def race_ids(self):
        return self.__discovered_race_ids

    @property
    def raw_race_cards(self):
        return self.__raw_race_cards


def main():
    persistence = RawRaceCardsPersistence()
    race_histories = RaceHistoryPersistence().load()

    while True:
        initial_raw_race_cards = persistence.load()
        raw_race_cards_collector = RawRaceCardsCollector(initial_raw_race_cards, n_races=10)

        #raw_race_cards_collector.collect_by_random_navigation(next_race_id="4632086")

        raw_race_cards_collector.collect_from_race_histories(race_histories)

        print(len(raw_race_cards_collector.raw_race_cards))
        persistence.save(raw_race_cards_collector.raw_race_cards)


if __name__ == '__main__':
    main()
