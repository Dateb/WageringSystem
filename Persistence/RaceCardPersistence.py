import json
import os
from typing import List

from DataAbstraction.RaceCard import RaceCard


class RaceCardsPersistence:
    def __init__(self, file_name: str):
        self.__base_file_name = file_name

    def save(self, race_cards: List[RaceCard]):
        raw_races = {str(race_card.date): {} for race_card in race_cards}
        for race_card in race_cards:
            raw_races[str(race_card.date)][race_card.title] = {}

        while race_cards:
            race_card = race_cards.pop(0)
            raw_races[str(race_card.date)][race_card.title][str(race_card.number)] = race_card.raw_race_card
            del race_card

        file_suffixes = {date[0:7] for date in raw_races}
        for file_suffix in file_suffixes:
            file_name = f"../data/train_test_race_cards/{self.__base_file_name}_{file_suffix}.json"
            if not os.path.isfile(file_name):
                raw_races_of_month = {}
            else:
                with open(file_name, "r") as f:
                    raw_races_of_month = json.load(f)

            new_raw_races_of_month = [(date, raw_races[date]) for date in raw_races if date[0:7] == file_suffix]
            for new_race in new_raw_races_of_month:
                raw_races_of_month[new_race[0]] = new_race[1]
            with open(file_name, "w") as f:
                json.dump(raw_races_of_month, f)

    def load_first_month(self) -> List[RaceCard]:
        race_cards_files = os.listdir("../data/train_test_race_cards")
        return self.__load_race_cards_of_file(race_cards_files[0])

    def load_every_month(self) -> List[RaceCard]:
        race_cards_files = os.listdir("../data/train_test_race_cards")
        race_cards = [self.__load_race_cards_of_file(race_cards_file) for race_cards_file in race_cards_files]

        return self.__flatten(race_cards)

    def __load_race_cards_of_file(self, file_name: str) -> List[RaceCard]:
        file_path = f"../data/train_test_race_cards/{file_name}"
        with open(file_path, "r") as f:
            raw_races = json.load(f)

        race_cards = []
        for date in raw_races:
            raw_races_of_date = raw_races[date]
            for track in raw_races_of_date:
                raw_races_of_date_track = raw_races_of_date[track]
                for race_number in raw_races_of_date_track:
                    raw_race = raw_races_of_date_track[race_number]
                    race_cards.append(RaceCard(raw_race["race"]["idRace"], raw_race, remove_non_starters=False))

        return race_cards

    def __flatten(self, xss):
        return [x for xs in xss for x in xs]


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_first_month()
    print(race_cards)
    print(race_cards[0].title)
    persistence.save(race_cards)


if __name__ == '__main__':
    main()
    print("finished")
