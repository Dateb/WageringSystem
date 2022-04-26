from typing import List

from SampleExtraction.FeatureManager import FeatureManager


class Horse:

    RUNNER_ID_KEY: str = "runner_id"
    RACE_ID_KEY: str = "race_id"
    PLACE_KEY: str = "place"
    RELEVANCE_KEY: str = "relevance"
    ATTRIBUTE_NAMES: List[str] = ["runner_id", "race_id", "track_id", "starting_odds", "place", "relevance"] + FeatureManager.FEATURE_NAMES

    def __init__(self,
                 runner_id: str,
                 race_id: str,
                 track_id: str,
                 starting_odds: float,
                 place: int,
                 features: dict,
                 ):

        self.__place = place
        self.__relevance = max([31 - place, 0])
        self.__data = {
            "runner_id": runner_id,
            "race_id": race_id,
            "track_id": track_id,
            "starting_odds": starting_odds,
            "place": place,
            "relevance": self.__relevance,
        }
        self.__data.update(features)

        self.__features = features

    @property
    def values(self) -> List:
        return list(self.__data.values())

    @property
    def runner_id(self):
        return self.__data["runner_id"]

    @property
    def race_id(self):
        return self.__data["race_id"]

    @property
    def place(self):
        return self.__place

    @property
    def starting_odds(self):
        return self.__data["starting_odds"]

