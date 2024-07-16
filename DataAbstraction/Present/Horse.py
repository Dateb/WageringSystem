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
    RANKING_LABEL_KEY: str = "ranking_label"
    WIN_PROB_LABEL_KEY: str = "win_probability"
    HAS_PLACED_LABEL_KEY: str = "has_placed"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        NAME_KEY, NUMBER_KEY, CURRENT_WIN_ODDS_KEY,
        CURRENT_PLACE_ODDS_KEY,
        PLACE_KEY,
        RANKING_LABEL_KEY, WIN_PROB_LABEL_KEY, HAS_PLACED_LABEL_KEY
    ]

    def __init__(self, raw_data: dict):
        self.competitors_beaten_probability = 0.0
        self.place_percentile = None
        self.relative_distance_behind = None
        self.uncorrected_momentum = -1
        self.momentum = None

        self.base_attributes = {}

        self.name = raw_data["name"]

        self.sire = raw_data["sire"]
        self.dam = raw_data["dam"]

        self.dam_sire = raw_data["damSire"]

        self.breeder = raw_data["breeder"]
        self.owner = raw_data["owner"]

        self.age = raw_data["age"]
        self.gender = raw_data["gender"]
        self.origin = raw_data["origin"]["iso"]
        if not self.origin:
            self.origin = "GB"

        self.number = raw_data["programNumber"]
        self.horse_id = raw_data["idRunner"]
        self.subject_id = raw_data["idSubject"]
        self.rating = raw_data["rating"]

        self.homeland = raw_data["homeland"]

        self.equipments = set()
        if "equipCode" in raw_data and raw_data["equipCode"]:
            self.equipments = set(raw_data["equipCode"].split("+"))

        self.place_racebets = self.__extract_place(raw_data)
        self.place = 0

        self.is_scratched = raw_data["scratched"]
        self.win_sp = self.__extract_betfair_win_odds(raw_data)
        if self.win_sp < 1:
            self.win_sp = self.__extract_racebets_win_odds(raw_data)

        self.sp_win_prob = 0

        self.place_sp = self.__extract_betfair_place_odds(raw_data)
        self.sp_place_prob = -1 if self.place_sp == 0 else 1 / self.place_sp

        # self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place_racebets == 1 else 0
        self.has_placed = 0
        self.ranking_label = 0

        self.pulled_up = 0
        if "resultFinishDNF" in raw_data:
            if raw_data["resultFinishDNF"] == "PU":
                self.pulled_up = 1

        self.horse_distance = -1

        self.lengths_behind = -1
        if "lengths_behind" in raw_data:
            self.lengths_behind = raw_data["lengths_behind"]

        self.jockey = Jockey(raw_data["jockey"])
        self.handicap_weight = self.jockey.weight
        if "handicap_weight" in raw_data:
            self.handicap_weight = round(raw_data["handicap_weight"], ndigits=1)

        self.jockey_id = self.jockey.id

        self.trainer = Trainer(raw_data["trainer"])

        self.trainer_id = self.trainer.id
        self.previous_performance = raw_data["ppString"].split(" - ")[0]

        self.result_finish_dnf = None
        if "resultFinishDNF" in raw_data:
            self.result_finish_dnf = raw_data["resultFinishDNF"]

        if "formTable" in raw_data:
            self.form_table = FormTable(raw_data["formTable"])
        else:
            self.form_table = FormTable([])

        self.base_attributes = {
            self.NAME_KEY: self.name,
            self.NUMBER_KEY: self.number,
            self.CURRENT_WIN_ODDS_KEY: self.win_sp,
            self.CURRENT_PLACE_ODDS_KEY: self.place_sp,
            self.PLACE_KEY: self.place,
            self.RANKING_LABEL_KEY: self.ranking_label,
            self.WIN_PROB_LABEL_KEY: self.sp_win_prob,
            self.HAS_PLACED_LABEL_KEY: self.has_placed
        }

        self.__features = {}
        self.finish_time = -1
        if "finishTime" in raw_data:
            if raw_data["finishTime"] is not None and self.place_racebets > 0:
                self.finish_time = float(raw_data["finishTime"])

    def set_betting_odds(self, new_odds: float):
        self.base_attributes[self.CURRENT_PLACE_ODDS_KEY] = new_odds

    def set_purse(self, purse: List[int]):
        self.purse = 0
        purse_idx = self.place_racebets - 1
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
        if self.is_scratched:
            return -1

        odds_of_horse = raw_data["odds"]
        if odds_of_horse["FXW"] == 0:
            return float(odds_of_horse["PRC"])
        return float(odds_of_horse["FXW"])

    def __extract_betfair_win_odds(self, raw_data: dict) -> float:
        if "bsp_win" not in raw_data:
            return -1
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
        self.__features[name] = value

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.__features.keys())

    @property
    def values(self) -> List:
        self.base_attributes.update(self.__features)
        return list(self.base_attributes.values())
