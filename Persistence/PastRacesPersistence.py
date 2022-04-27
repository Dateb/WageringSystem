import json

from SampleExtraction.PastRacesContainer import PastRacesContainer


class PastRacesPersistence:
    def __init__(self):
        self.__FILE_NAME = "../data/past_races.json"

    def save(self, raw_past_races: dict):
        print("writing...")
        json.dump(raw_past_races, open(self.__FILE_NAME, "w"))
        print("writing done")

    def load(self) -> PastRacesContainer:
        with open(self.__FILE_NAME, "r") as f:
            raw_past_races = json.load(f)

        return PastRacesContainer(raw_past_races)
