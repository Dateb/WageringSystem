import json
from typing import List

from DataCollection.RaceCardsCollector import RaceCardsCollector
from Persistence.RaceCardPersistence import RaceCardsPersistence


class TestDataCollector:

    INITIAL_ODDS_FILE_NAME = "../data/initial_odds.json"

    def __init__(self):
        self.__race_cards_persistence = RaceCardsPersistence(data_dir_name="test_race_cards")
        self.__initial_race_cards = self.__race_cards_persistence.load_every_month_non_writable()

        self.__race_cards_collector = RaceCardsCollector([], remove_non_starters=False)

        with open(self.INITIAL_ODDS_FILE_NAME) as file:
            self.__initial_odds = json.load(file)

    def update_collection(self):
        new_race_ids = self.__get_new_race_ids()
        new_race_cards = self.__race_cards_collector.collect_final_full_race_cards_from_race_ids(new_race_ids)

        for new_race_card in new_race_cards:
            initial_odds_of_race = self.__initial_odds[new_race_card.race_id]
            horses_to_remove = []
            for horse in new_race_card.horses:
                if horse not in initial_odds_of_race:
                    horses_to_remove.append(horse)
                else:
                    initial_odds_of_horse = initial_odds_of_race[horse]
                    new_race_card.set_odds_of_horse(horse, initial_odds_of_horse)
            for horse_to_remove in horses_to_remove:
                new_race_card.remove_horse(horse_to_remove)

        self.__race_cards_persistence.save(self.__initial_race_cards + new_race_cards)

    def __get_new_race_ids(self) -> List[str]:
        test_race_ids = set(self.__initial_odds.keys())
        collected_race_ids = {race_card.race_id for race_card in self.__initial_race_cards}

        return list(test_race_ids.difference(collected_race_ids))


def main():
    test_data_collector = TestDataCollector()
    test_data_collector.update_collection()


if __name__ == "__main__":
    main()
