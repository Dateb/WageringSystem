import json
import os
from typing import List, Dict
from DataAbstraction.Present.WritableRaceCard import RaceCard, WritableRaceCard


class RaceCardsPersistence:
    def __init__(self, data_dir_name: str):
        self.__data_dir_name = data_dir_name
        self.__dir_path = f"../data/{self.__data_dir_name}"
        if os.path.isdir(self.__dir_path):
            self.race_card_file_names = sorted(os.listdir(self.__dir_path))
        else:
            self.race_card_file_names = []
            os.makedirs(self.__dir_path)
        self.__iter_idx = 0

    def save(self, race_cards: List[WritableRaceCard]):
        print("writing...")
        raw_races = {str(race_card.date): {} for race_card in race_cards}
        for race_card in race_cards:
            raw_races[str(race_card.date)][race_card.track_name] = {}

        while race_cards:
            race_card = race_cards.pop(0)
            raw_races[str(race_card.date)][race_card.track_name][str(race_card.race_number)] = race_card.raw_race_card
            del race_card

        file_suffixes = {date[0:7] for date in raw_races}
        for file_suffix in file_suffixes:
            file_name = f"{self.__data_dir_name}_{file_suffix}.json"
            path_name = f"{self.__dir_path}/{file_name}"
            if not os.path.isfile(path_name):
                raw_races_of_month = {}
                self.race_card_file_names.append(file_name)
            else:
                with open(path_name, "r") as f:
                    raw_races_of_month = json.load(f)

            new_raw_races_of_month = [(date, raw_races[date]) for date in raw_races if date[0:7] == file_suffix]
            for new_race in new_raw_races_of_month:
                raw_races_of_month[new_race[0]] = new_race[1]
            with open(path_name, "w") as f:
                json.dump(raw_races_of_month, f)
        print("writing done")

    def load_race_card_files_non_writable(self, race_card_file_names: List[str]) -> Dict[str, RaceCard]:
        race_cards_per_file = [
            self.__load_race_cards_of_file(race_card_file_name, self.__create_race_card)
            for race_card_file_name in race_card_file_names
        ]
        total_race_cards = {}
        for race_cards in race_cards_per_file:
            total_race_cards = {**total_race_cards, **race_cards}

        return total_race_cards

    def load_first_month_non_writable(self) -> Dict[str, RaceCard]:
        return self.__load_race_cards_of_file(self.race_card_file_names[1], self.__create_race_card)

    def load_every_month_non_writable(self) -> Dict[str, RaceCard]:
        return self.load_race_card_files_non_writable(self.race_card_file_names)

    def load_first_month_writable(self) -> Dict[str, WritableRaceCard]:
        return self.__load_race_cards_of_file(self.race_card_file_names[1], self.__create_writable_race_card)

    def load_every_month_writable(self) -> Dict[str, WritableRaceCard]:
        race_cards_per_file = [
            self.__load_race_cards_of_file(race_card_file_name, self.__create_writable_race_card)
            for race_card_file_name in self.race_card_file_names
        ]
        total_race_cards = {}
        for race_cards in race_cards_per_file:
            total_race_cards = {**total_race_cards, **race_cards}

        return total_race_cards

    def __load_race_cards_of_file(self, file_name: str, race_card_creation):
        file_path = f"../data/{self.__data_dir_name}/{file_name}"
        with open(file_path, "r") as f:
            raw_races = json.load(f)

        race_cards = {}
        for date in raw_races:
            raw_races_of_date = raw_races[date]
            for track in raw_races_of_date:
                raw_races_of_date_track = raw_races_of_date[track]
                for race_number in raw_races_of_date_track:
                    raw_race = raw_races_of_date_track[race_number]
                    new_race_card = race_card_creation(raw_race)
                    race_cards[str(new_race_card.datetime)] = new_race_card

        return race_cards

    def __create_race_card(self, raw_race: dict) -> RaceCard:
        return RaceCard(raw_race["race"]["idRace"], raw_race, remove_non_starters=True)

    def __create_writable_race_card(self, raw_race: dict) -> RaceCard:
        return WritableRaceCard(raw_race["race"]["idRace"], raw_race, remove_non_starters=True)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__iter_idx >= len(self.race_card_file_names):
            raise StopIteration

        race_cards = self.__load_race_cards_of_file(
            self.race_card_file_names[self.__iter_idx],
            self.__create_writable_race_card
        )

        self.__iter_idx += 1
        return race_cards


def main():
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_first_month_non_writable()
    print(race_cards)
    print(race_cards[0].track_name)
    #persistence.save(race_cards)


if __name__ == '__main__':
    main()
    print("finished")
