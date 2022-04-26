import json
from typing import List

from DataCollection.RawRaceCard import RawRaceCard


class RawRaceCardsPersistence:
    def __init__(self):
        self.__FILE_NAME = "../data/raw_race_cards.json"

    def save(self, raw_race_cards: List[RawRaceCard]):
        raw_race_cards_json = {}
        for raw_race_card in raw_race_cards:
            raw_race_cards_json[raw_race_card.race_id] = raw_race_card.raw_race_data

        print("writing...")
        with open(self.__FILE_NAME, "w") as f:
            json.dump(raw_race_cards_json, f)
        print("writing done")

    def load(self) -> List[RawRaceCard]:
        with open(self.__FILE_NAME, "r") as f:
            raw_race_cards_json = json.load(f)

        raw_race_cards = [RawRaceCard(race_id, raw_race_cards_json[race_id]) for race_id in raw_race_cards_json]

        return raw_race_cards
