import json
import os
from typing import List

from DataCollection.RawRaceCard import RawRaceCard


class RawRaceCardsPersistence:
    def __init__(self, file_name: str):
        self.__FILE_NAME = f"../data/{file_name}.json"

    def save(self, raw_race_cards: List[RawRaceCard]):
        raw_race_cards_json = {}
        for raw_race_card in raw_race_cards:
            raw_race_cards_json[raw_race_card.race_id] = raw_race_card.raw_race_data

        print("writing...")
        with open(self.__FILE_NAME, "w") as f:
            json.dump(raw_race_cards_json, f)
        print("writing done")

    def load(self) -> List[RawRaceCard]:
        if not os.path.isfile(self.__FILE_NAME):
            print("File not found. Returning empty list.")
            return []

        with open(self.__FILE_NAME, "r") as f:
            raw_race_cards_json = json.load(f)

        raw_race_cards = [RawRaceCard(race_id, raw_race_cards_json[race_id]) for race_id in raw_race_cards_json]

        return raw_race_cards
