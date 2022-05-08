import json
import os
from typing import List

from DataAbstraction.RaceCard import RaceCard


class RaceCardsPersistence:
    def __init__(self, file_name: str):
        self.__FILE_NAME = f"../data/{file_name}.json"

    def save(self, race_cards: List[RaceCard]):
        raw_races = {}
        for race_card in race_cards:
            raw_races[race_card.race_id] = race_card.raw_race_card

        print("writing...")
        with open(self.__FILE_NAME, "w") as f:
            json.dump(raw_races, f)
        print("writing done")

    def load(self) -> List[RaceCard]:
        raw_races = self.load_raw()
        return [RaceCard(race_id, raw_races[race_id]) for race_id in raw_races]

    def load_raw(self) -> dict:
        if not os.path.isfile(self.__FILE_NAME):
            print("File not found. Returning empty dict.")
            return {}

        with open(self.__FILE_NAME, "r") as f:
            raw_races = json.load(f)

        return raw_races
