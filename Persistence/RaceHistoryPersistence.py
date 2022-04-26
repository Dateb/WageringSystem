import json
from typing import List

from DataCollection.RaceHistory import RaceHistory


class RaceHistoryPersistence:
    def __init__(self):
        self.__FILE_NAME = "../data/race_histories.json"

    def save(self, race_histories: List[RaceHistory]):
        race_histories_json = {}
        for race_history in race_histories:
            race_histories_json[race_history.subject_id] = race_history.race_ids

        print("writing...")
        json.dump(race_histories_json, open(self.__FILE_NAME, "w"))
        print("writing done")

    def load(self) -> List[RaceHistory]:
        with open(self.__FILE_NAME, "r") as f:
            race_histories_json = json.load(f)

        race_histories = [RaceHistory(subject_id, race_histories_json[subject_id])
                          for subject_id in race_histories_json]

        return race_histories
