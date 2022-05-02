import json

from DataCollection.RawRaceCard import RawRaceCard
from SampleExtraction.RaceCard import RaceCard


class RaceCardsPersistence:
    def __init__(self, file_name: str):
        self.__FILE_NAME = f"../data/{file_name}.json"

    def load(self) -> dict:
        with open(self.__FILE_NAME, "r") as f:
            raw_race_cards_json = json.load(f)

        raw_race_cards = [RawRaceCard(race_id, raw_race_cards_json[race_id]) for race_id in raw_race_cards_json]
        race_cards = {}
        for raw_race_card in raw_race_cards:
            race_cards[raw_race_card.race_id] = RaceCard(raw_race_card)

        return race_cards
