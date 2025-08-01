import random
from typing import List

from DataAbstraction.Past.FormTable import FormTable
from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.Trainer import Trainer


class Horse:

    NAME_KEY: str = "name"
    NUMBER_KEY: str = "number"
    PLACE_KEY: str = "place"
    CURRENT_WIN_ODDS_KEY: str = "current_win_odds"
    CURRENT_PLACE_ODDS_KEY: str = "current_place_odds"
    KELLY_FRACTION_KEY: str = "kelly_fraction"
    ODDS_SHIFT: str = "odds_shift"
    LABEL: str = "label"
    WIN_PROBABILITY_KEY: str = "win_probability"
    BASE_EXPECTED_VALUE_KEY: str = "base_expected_value"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        NAME_KEY, NUMBER_KEY, CURRENT_WIN_ODDS_KEY,
        CURRENT_PLACE_ODDS_KEY,
        PLACE_KEY, ODDS_SHIFT, LABEL,
    ]

    def __init__(self, raw_data: dict):
        self.base_attributes = {}

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
        self.homeland = raw_data["homeland"]

        self.equipments = []
        if "equipCode" in raw_data and raw_data["equipCode"]:
            self.equipments = raw_data["equipCode"].split("+")

        self.place = self.__extract_place(raw_data)
        self.relevance = 0

        self.racebets_win_sp = self.__extract_racebets_win_odds(raw_data)
        self.betfair_win_sp = self.__extract_betfair_win_odds(raw_data)
        self.betfair_place_sp = self.__extract_betfair_place_odds(raw_data)

        self.probability_shift = random.normalvariate(mu=0, sigma=0.1)

        self.shifted_odds = 0
        if self.betfair_place_sp:
            self.shifted_odds = 1 / ((1 / self.betfair_place_sp) * (1 + self.probability_shift))

        self.label = int(self.probability_shift < 0)

        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0
        self.horse_distance = self.__extract_horse_distance(raw_data)

        self.jockey = Jockey(raw_data["jockey"])
        self.weight_category = round(self.jockey.weight / 2) * 2

        jockey_first_name = raw_data["jockey"]["firstName"]
        jockey_last_name = raw_data["jockey"]["lastName"]

        self.jockey_name = f"{jockey_first_name} {jockey_last_name}"

        self.trainer = Trainer(raw_data["trainer"])

        trainer_first_name = raw_data["trainer"]["firstName"]
        trainer_last_name = raw_data["trainer"]["lastName"]

        self.trainer_name = f"{trainer_first_name} {trainer_last_name}"

        self.is_scratched = raw_data["scratched"]
        self.previous_performance = raw_data["ppString"].split(" - ")[0]

        if "formTable" in raw_data:
            self.form_table = FormTable(raw_data["formTable"])
        else:
            self.form_table = FormTable([])

        self.base_attributes = {
            self.NAME_KEY: self.name,
            self.NUMBER_KEY: self.number,
            self.CURRENT_WIN_ODDS_KEY: self.racebets_win_sp,
            self.CURRENT_PLACE_ODDS_KEY: self.betfair_place_sp,
            self.PLACE_KEY: self.place,
            self.ODDS_SHIFT: self.probability_shift,
            self.LABEL: self.label,
        }

        self.features = {}
        self.speed_figure = None

    def set_betting_odds(self, new_odds: float):
        self.base_attributes[self.CURRENT_PLACE_ODDS_KEY] = new_odds

    def set_purse(self, purse: List[int]):
        self.purse = 0
        purse_idx = self.place - 1
        if len(purse) > purse_idx >= 0:
            self.purse = purse[purse_idx]

    def __extract_place(self, raw_data: dict):
        if raw_data["scratched"] or 'finalPosition' not in raw_data:
            return -1

        if 'finalPosition' in raw_data:
            return int(raw_data["finalPosition"])

    def __extract_horse_distance(self, raw_data: dict):
        if self.has_won:
            return 0

        if raw_data["scratched"]:
            return -1

        if 'horseDistance' in raw_data:
            return float(raw_data["horseDistance"])

        return -1

    def __extract_racebets_win_odds(self, raw_data: dict):
        odds_of_horse = raw_data["odds"]
        if odds_of_horse["FXW"] == 0:
            return float(odds_of_horse["PRC"])
        return float(odds_of_horse["FXW"])

    def __extract_betfair_win_odds(self, raw_data: dict) -> float:
        if "bsp_win" not in raw_data:
            return 0
        return raw_data["bsp_win"]

    def __extract_betfair_place_odds(self, raw_data: dict):
        if "bsp_place" not in raw_data:
            return 0
        return raw_data["bsp_place"]

    def __extract_post_position(self, raw_data: dict) -> int:
        if "postPosition" in raw_data:
            return int(raw_data["postPosition"])
        return -1

    def set_feature_value(self, name: str, value):
        self.features[name] = value

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.features.keys())

    @property
    def feature_values(self) -> List:
        return list(self.features.values())

    @property
    def values(self) -> List:
        self.base_attributes.update(self.features)
        return list(self.base_attributes.values())
