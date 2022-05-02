import json
import os

from DataCollection.PastRacesContainer import PastRacesContainer


class PastRacesContainerPersistence:
    def __init__(self, file_name: str):
        self.__FILE_NAME = f"../data/{file_name}.json"

    def save(self, raw_past_races: dict):
        print("writing...")
        json.dump(raw_past_races, open(self.__FILE_NAME, "w"))
        print("writing done")

    def load(self) -> PastRacesContainer:
        if not os.path.isfile(self.__FILE_NAME):
            print("File not found. Returning empty past races container.")
            return PastRacesContainer(raw_past_races={})

        with open(self.__FILE_NAME, "r") as f:
            raw_past_races = json.load(f)
            return PastRacesContainer(raw_past_races)
