from math import floor
from typing import List

from scipy.stats import percentileofscore

from DataAbstraction.Past.FormTable import FormTable
from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.Trainer import Trainer
from util.speed_calculator import get_speed_figures_distribution


class Horse:

    NAME_KEY: str = "name"
    NUMBER_KEY: str = "number"
    PLACE_KEY: str = "place"
    CURRENT_ESTIMATION_WIN_ODDS_KEY: str = "current_estimation_odds"
    CURRENT_BETTING_WIN_ODDS_KEY: str = "current_betting_odds"
    CURRENT_PLACE_ODDS_KEY: str = "current_place_odds"
    KELLY_FRACTION_KEY: str = "kelly_fraction"
    RELEVANCE_KEY: str = "relevance"
    WIN_PROBABILITY_KEY: str = "win_probability"
    BASE_EXPECTED_VALUE_KEY: str = "base_expected_value"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        NAME_KEY, NUMBER_KEY,
        CURRENT_ESTIMATION_WIN_ODDS_KEY, CURRENT_BETTING_WIN_ODDS_KEY,
        CURRENT_PLACE_ODDS_KEY,
        PLACE_KEY, RELEVANCE_KEY,
    ]

    def __init__(self, raw_data: dict):
        self.__base_attributes = {}

        self.name = raw_data["name"]
        self.sire = raw_data["sire"]
        self.dam = raw_data["dam"]
        self.dam_sire = raw_data["damSire"]
        self.breeder = raw_data["breeder"]
        self.owner = raw_data["owner"]
        self.age = raw_data["age"]
        self.gender = raw_data["gender"]
        self.number = raw_data["programNumber"]
        self.horse_id = raw_data["idRunner"]
        self.subject_id = raw_data["idSubject"]
        self.rating = raw_data["rating"]

        self.equipments = []
        if "equipCode" in raw_data and raw_data["equipCode"]:
            self.equipments = raw_data["equipCode"].split("+")

        self.horse_distance = self.__extract_horse_distance(raw_data)
        self.place = self.__extract_place(raw_data)
        self.relevance = 0
        self.set_estimation_win_odds(self.__extract_current_win_odds(raw_data))

        self.current_place_odds = self.__extract_current_place_odds(raw_data)
        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0

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
            self.NAME_KEY: self.name,
            self.NUMBER_KEY: self.number,
            self.CURRENT_ESTIMATION_WIN_ODDS_KEY: self.current_win_odds,
            self.CURRENT_BETTING_WIN_ODDS_KEY: self.current_win_odds,
            self.CURRENT_PLACE_ODDS_KEY: self.current_place_odds,
            self.PLACE_KEY: self.place,
            self.RELEVANCE_KEY: self.relevance,
        }

        self.__features = {}

    def set_estimation_win_odds(self, new_odds: float):
        self.current_win_odds = new_odds
        self.__base_attributes[self.CURRENT_ESTIMATION_WIN_ODDS_KEY] = new_odds

        self.inverse_win_odds = 0
        if self.current_win_odds != 0:
            self.inverse_win_odds = 1 / self.current_win_odds

    def set_betting_win_odds(self, new_odds: float):
        self.__base_attributes[self.CURRENT_BETTING_WIN_ODDS_KEY] = new_odds

    def set_relevance(self, speed_figure: float):
        if speed_figure:
            score_percentile = percentileofscore(get_speed_figures_distribution(), speed_figure) / 100
            self.relevance = floor(score_percentile * 29) + self.has_won

        self.__base_attributes[self.RELEVANCE_KEY] = self.relevance

    def set_purse(self, purse: List[int]):
        self.purse = 0
        purse_idx = self.place - 1
        if len(purse) > purse_idx >= 0:
            self.purse = purse[purse_idx]

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
