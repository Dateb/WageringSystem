from math import ceil
from typing import List

from DataAbstraction.Past.FormTable import FormTable
from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.Trainer import Trainer


class Horse:

    HORSE_ID_KEY: str = "horse_id"
    PLACE_KEY: str = "place"
    CURRENT_WIN_ODDS_KEY: str = "current_odds"
    CURRENT_PLACE_ODDS_KEY: str = "current_place_odds"
    KELLY_FRACTION_KEY: str = "kelly_fraction"
    RELEVANCE_KEY: str = "relevance"
    WIN_PROBABILITY_KEY: str = "win_probability"
    BASE_EXPECTED_VALUE_KEY: str = "base_expected_value"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        HORSE_ID_KEY, CURRENT_WIN_ODDS_KEY, CURRENT_PLACE_ODDS_KEY, PLACE_KEY, RELEVANCE_KEY,
    ]

    def __init__(self, raw_data: dict):
        self.name = raw_data["name"]
        self.sire = raw_data["sire"]
        self.breeder = raw_data["breeder"]
        self.owner = raw_data["owner"]
        self.age = raw_data["age"]
        self.gender = raw_data["gender"]
        self.horse_id = raw_data["idRunner"]
        self.subject_id = raw_data["idSubject"]
        self.rating = raw_data["rating"]
        self.horse_distance = self.__extract_horse_distance(raw_data)
        self.place = self.__extract_place(raw_data)
        self.current_win_odds = self.__extract_current_win_odds(raw_data)
        self.current_place_odds = self.__extract_current_place_odds(raw_data)
        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0

        self.has_blinkers = raw_data["blinkers"]
        self.jockey = Jockey(raw_data["jockey"])

        jockey_first_name = raw_data["jockey"]["firstName"]
        jockey_last_name = raw_data["jockey"]["lastName"]

        self.jockey_name = f"{jockey_first_name} {jockey_last_name}"

        self.trainer = Trainer(raw_data["trainer"])

        trainer_first_name = raw_data["trainer"]["firstName"]
        trainer_last_name = raw_data["trainer"]["lastName"]

        self.trainer_name = f"{trainer_first_name} {trainer_last_name}"

        self.is_scratched = raw_data["scratched"]
        self.past_performance = raw_data["ppString"]

        if "formTable" in raw_data:
            self.form_table = FormTable(raw_data["formTable"])
        else:
            self.form_table = FormTable([])

        self.__base_attributes = {
            self.HORSE_ID_KEY: self.horse_id,
            self.CURRENT_WIN_ODDS_KEY: self.current_win_odds,
            self.CURRENT_PLACE_ODDS_KEY: self.current_place_odds,
            self.PLACE_KEY: self.place,
        }

        self.__features = {}

    def set_relevance(self, race_distance: float):
        self.relevance = 0
        if self.horse_distance >= 0:
            percentage_behind_winner = self.horse_distance * 2.4 / race_distance
            self.relevance = max(3 - ceil(percentage_behind_winner * 200), 0)

        self.__base_attributes[self.RELEVANCE_KEY] = self.relevance

    def __extract_place(self, raw_data: dict):
        if raw_data["scratched"]:
            return -1

        if 'finalPosition' in raw_data:
            return int(raw_data["finalPosition"])

        return -1

    def __extract_horse_distance(self, raw_data: dict):
        if raw_data["scratched"]:
            return -1

        if 'horseDistance' in raw_data:
            return float(raw_data["horseDistance"])

        return -1

    def __extract_current_win_odds(self, raw_data: dict):
        odds_of_horse = raw_data["odds"]
        if odds_of_horse["FXW"] == 0:
            return float(odds_of_horse["PRC"])
        return float(odds_of_horse["FXW"])

    def __extract_current_place_odds(self, raw_data: dict):
        odds_of_horse = raw_data["odds"]
        return odds_of_horse["FXP"]

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
