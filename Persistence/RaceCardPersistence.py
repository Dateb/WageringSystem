import json
import os
import pathlib
from typing import List, Dict
from DataAbstraction.Present.WritableRaceCard import RaceCard, WritableRaceCard


class RaceDataPersistence:
    def __init__(self, data_dir_name: str):
        path_of_this_file = pathlib.Path(__file__).parent.resolve()
        self.__data_dir_name = data_dir_name
        self.__dir_path = f"{str(path_of_this_file)}/../data/{self.__data_dir_name}"
        if os.path.isdir(self.__dir_path):
            self.race_data_file_names = sorted(os.listdir(self.__dir_path))
        else:
            self.race_data_file_names = []
            os.makedirs(self.__dir_path)
        self.iter_idx = 0

    def save(self, race_cards: List[WritableRaceCard]):
        raw_races = {str(race_card.date): {} for race_card in race_cards}
        for race_card in race_cards:
            raw_races[str(race_card.date)][race_card.track_name] = {}

        while race_cards:
            race_card = race_cards.pop(0)
            raw_races[str(race_card.date)][race_card.track_name][str(race_card.race_number)] = race_card.raw_race_card
            del race_card

        self.save_date_based_dict(raw_races)

    def save_date_based_dict(self, date_based_dict: dict) -> None:
        print("writing...")
        file_names = {date[0:7] for date in date_based_dict}
        for file_name in file_names:
            path_name = f"{self.__dir_path}/{file_name}.json"
            if not os.path.isfile(path_name):
                raw_races_of_month = {}
                self.race_data_file_names.append(file_name)
            else:
                with open(path_name, "r") as f:
                    raw_races_of_month = json.load(f)

            new_raw_races_of_month = [(date, date_based_dict[date]) for date in date_based_dict if date[0:7] == file_name]
            for new_race in new_raw_races_of_month:
                raw_races_of_month[new_race[0]] = new_race[1]

            with open(path_name, "w") as f:
                json.dump(raw_races_of_month, f)
        print("writing done")

    def load_race_card_files_non_writable(self, race_card_file_names: List[str]) -> Dict[str, RaceCard]:
        race_cards_per_file = []
        for race_card_file_name in race_card_file_names:
            raw_races = self.load_race_data(race_card_file_name)
            race_cards_per_file.append(self.raw_races_to_race_cards(raw_races, self.create_race_card))

        total_race_cards = {}
        for race_cards in race_cards_per_file:
            total_race_cards = {**total_race_cards, **race_cards}

        return total_race_cards

    def load_race_card_files_writable(self, race_card_file_names: List[str]) -> Dict[str, WritableRaceCard]:
        race_cards_per_file = [
            self.raw_races_to_race_cards(race_card_file_name, self.create_writable_race_card)
            for race_card_file_name in race_card_file_names
        ]
        total_race_cards = {}
        for race_cards in race_cards_per_file:
            total_race_cards = {**total_race_cards, **race_cards}

        return total_race_cards

    def load_first_month_non_writable(self) -> Dict[str, RaceCard]:
        return self.raw_races_to_race_cards(self.race_data_file_names[1], self.create_race_card)

    def load_every_month_non_writable(self) -> Dict[str, RaceCard]:
        return self.load_race_card_files_non_writable(self.race_data_file_names)

    def load_first_month_writable(self) -> Dict[str, WritableRaceCard]:
        return self.raw_races_to_race_cards(self.race_data_file_names[0], self.create_writable_race_card)

    def load_every_month_writable(self) -> Dict[str, WritableRaceCard]:
        race_cards_per_file = [
            self.raw_races_to_race_cards(race_card_file_name, self.create_writable_race_card)
            for race_card_file_name in self.race_data_file_names
        ]
        total_race_cards = {}
        for race_cards in race_cards_per_file:
            total_race_cards = {**total_race_cards, **race_cards}

        return total_race_cards

    def raw_races_to_race_cards(self, raw_races: dict, race_card_creation):
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

    def load_race_data(self, file_name: str) -> dict:
        file_path = f"{self.__dir_path}/{file_name}"
        if not os.path.isfile(file_path):
            return {}
        with open(file_path, "r") as f:
            return json.load(f)

    def create_race_card(self, raw_race: dict) -> RaceCard:
        return RaceCard(raw_race["race"]["idRace"], raw_race, remove_non_starters=True)

    def create_writable_race_card(self, raw_race: dict) -> RaceCard:
        return WritableRaceCard(raw_race["race"]["idRace"], raw_race, remove_non_starters=True)

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_idx >= len(self.race_data_file_names):
            self.iter_idx = 0
            raise StopIteration

        race_data = self.load_race_data(self.race_data_file_names[self.iter_idx])

        self.iter_idx += 1
        return race_data


def main():
    persistence = RaceDataPersistence("train_race_cards")
    race_cards = persistence.load_first_month_non_writable()
    print(race_cards)
    print(race_cards[0].track_name)
    #persistence.save(race_cards)


if __name__ == '__main__':
    main()
    print("finished")
