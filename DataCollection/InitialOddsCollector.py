import json
import os

from DataCollection.DayCollector import DayCollector
from DataCollection.RaceCardsCollector import RaceCardsCollector


class InitialOddsCollector:

    FILE_NAME = "../data/initial_odds.json"

    def __init__(self):
        if not os.path.isfile(self.FILE_NAME):
            print("Initial odds not found")
            self.__initial_odds = {}
        else:
            with open(self.FILE_NAME) as file:
                self.__initial_odds = json.load(file)
        self.__day_collector = DayCollector()
        self.__race_cards_collector = RaceCardsCollector([])

    def collect_initial_odds_from_tomorrow_races(self) -> None:
        race_ids = self.__day_collector.get_race_ids_of_tomorrow()
        race_cards = self.__race_cards_collector.collect_base_race_cards_from_race_ids(race_ids)
        for race_card in race_cards:
            self.__initial_odds[race_card.race_id] = {horse: race_card.get_current_odds_of_horse(horse) for horse in race_card.horses}

        with open(self.FILE_NAME, "w") as file:
            json.dump(self.__initial_odds, file)


def main():
    initial_odds_collector = InitialOddsCollector()
    initial_odds_collector.collect_initial_odds_from_tomorrow_races()


if __name__ == '__main__':
    main()
