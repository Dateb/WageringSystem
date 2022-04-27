import json


class PastRacesPersistence:
    def __init__(self):
        self.__FILE_NAME = "../data/past_races.json"

    def save(self, past_races: dict):
        print("writing...")
        json.dump(past_races, open(self.__FILE_NAME, "w"))
        print("writing done")

    def load(self) -> dict:
        with open(self.__FILE_NAME, "r") as f:
            past_races = json.load(f)

        return past_races
