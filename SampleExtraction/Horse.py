from typing import List


class Horse:

    HORSE_ID_KEY: str = "horse_id"
    RACE_ID_KEY: str = "race_id"
    PLACE_KEY: str = "place"
    RELEVANCE_KEY: str = "relevance"
    BASE_ATTRIBUTE_NAMES: List[str] = ["horse_id", "race_id", "track_id", "starting_odds", "place", "relevance"]

    def __init__(self,
                 raw_data: dict,
                 horse_id: str,
                 race_id: str,
                 track_id: str,
                 starting_odds: float,
                 place: int,
                 ):

        self.__raw_data = raw_data
        self.__place = place
        self.__relevance = max([31 - place, 0])
        self.__data = {
            "horse_id": horse_id,
            "race_id": race_id,
            "track_id": track_id,
            "starting_odds": starting_odds,
            "place": place,
            "relevance": self.__relevance,
        }

        self.__features = {}

    def set_feature(self, name: str, value):
        self.__features[name] = value

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.__features.keys())

    @property
    def raw_data(self) -> dict:
        return self.__raw_data

    @property
    def values(self) -> List:
        self.__data.update(self.__features)
        return list(self.__data.values())

    @property
    def horse_id(self):
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

