from datetime import datetime
from typing import List

from DataAbstraction.Past.PastHorse import PastHorse


class PastRaceCard:

    def __init__(self, raw_race_card: dict, remove_non_starters: bool):
        self.__extract_attributes(raw_race_card)
        if remove_non_starters:
            self.__remove_non_starters()

    def __extract_attributes(self, raw_race_card: dict):
        self.__extract_horses(raw_race_card["runners"]["data"])
        self.__extract_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]
        result = raw_race_card["result"]

        self.title = event["title"]
        self.race_id = race["idRace"]
        self.number = race["raceNumber"]
        self.distance = race["distance"]
        self.race_class = race["categoryLetter"]
        self.winner_id = str(result["positions"][0]["idRunner"])

    def __extract_horses(self, raw_horses: dict):
        self.horses: List[PastHorse] = [PastHorse(raw_horses[horse_id]) for horse_id in raw_horses]

    def __extract_date(self, raw_race_card: dict):
        self.date_raw = raw_race_card["race"]["postTime"]
        self.datetime = datetime.fromtimestamp(self.date_raw)
        self.date = self.datetime.date()

    def __remove_non_starters(self):
        self.horses = [horse for horse in self.horses if not horse.is_scratched]

    def get_subject(self, subject_id: str) -> PastHorse:
        for horse in self.horses:
            if horse.subject_id == subject_id:
                return horse
