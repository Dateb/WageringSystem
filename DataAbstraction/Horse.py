from typing import List

from DataAbstraction.FormTable import FormTable
from DataAbstraction.Jockey import Jockey


class Horse:

    HORSE_ID_KEY: str = "horse_id"
    PLACE_KEY: str = "place"
    RELEVANCE_KEY: str = "relevance"
    CURRENT_ODDS_KEY: str = "current_odds"
    HAS_WON_KEY: str = "has_won"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        HORSE_ID_KEY, CURRENT_ODDS_KEY, PLACE_KEY, RELEVANCE_KEY, HAS_WON_KEY,
    ]

    def __init__(self, raw_data: dict):
        self.name = raw_data["name"]
        self.age = raw_data["age"]
        self.horse_id = raw_data["idRunner"]
        self.subject_id = raw_data["idSubject"]
        self.place = self.__extract_place(raw_data)
        self.current_odds = self.__extract_current_odds(raw_data)
        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0
        self.relevance = self.has_won# max(31 - self.place, 0)
        self.jockey = Jockey(raw_data["jockey"])
        self.form_table = FormTable(raw_data["formTable"])

        self.__base_attributes = {
            self.HORSE_ID_KEY: self.horse_id,
            self.CURRENT_ODDS_KEY: self.current_odds,
            self.PLACE_KEY: self.place,
            self.RELEVANCE_KEY: self.relevance,
            self.HAS_WON_KEY: self.has_won,
        }

        self.__features = {}

    def __extract_place(self, raw_data: dict):
        if raw_data["scratched"]:
            return -1

        if 'finalPosition' in raw_data:
            return int(raw_data["finalPosition"])

        return 100

    def __extract_current_odds(self, raw_data: dict):
        odds_of_horse = raw_data["odds"]
        if odds_of_horse["FXW"] == 0:
            return float(odds_of_horse["PRC"])
        return float(odds_of_horse["FXW"])

    def __extract_post_position(self, raw_data: dict) -> int:
        if "postPosition" in raw_data:
            return int(raw_data["postPosition"])
        return -1

    def set_feature_value(self, name: str, value):
        self.__features[name] = value

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.__features.keys())

    @property
    def values(self) -> List:
        self.__base_attributes.update(self.__features)
        return list(self.__base_attributes.values())
