from typing import List

from DataAbstraction.Past.FormTable import FormTable
from DataAbstraction.Past.PastRaceCard import PastRaceCard
from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.Trainer import Trainer


class Horse:

    HORSE_ID_KEY: str = "horse_id"
    PLACE_KEY: str = "place"
    CURRENT_WIN_ODDS_KEY: str = "current_odds"
    CURRENT_PLACE_ODDS_KEY: str = "current_place_odds"
    HAS_WON_KEY: str = "has_won"
    KELLY_FRACTION_KEY: str = "kelly_fraction"
    RELEVANCE_KEY: str = "relevance"
    BASE_ATTRIBUTE_NAMES: List[str] = [
        HORSE_ID_KEY, CURRENT_WIN_ODDS_KEY, CURRENT_PLACE_ODDS_KEY, PLACE_KEY, HAS_WON_KEY, RELEVANCE_KEY,
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
        self.place = self.__extract_place(raw_data)
        self.current_win_odds = self.__extract_current_win_odds(raw_data)
        self.current_place_odds = self.__extract_current_place_odds(raw_data)
        self.post_position = self.__extract_post_position(raw_data)
        self.has_won = 1 if self.place == 1 else 0
        self.relevance = 0 if self.place == -1 else max([4 - self.place, 0])
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

        self.past_races = []
        if "pastRaces" in raw_data:
            self.past_races = [
                PastRaceCard(raw_past_race, remove_non_starters=True) for raw_past_race in raw_data["pastRaces"]
            ]

        if "formTable" in raw_data:
            self.form_table = FormTable(raw_data["formTable"])
        else:
            self.form_table = FormTable([])

        self.__base_attributes = {
            self.HORSE_ID_KEY: self.horse_id,
            self.CURRENT_WIN_ODDS_KEY: self.current_win_odds,
            self.CURRENT_PLACE_ODDS_KEY: self.current_place_odds,
            self.PLACE_KEY: self.place,
            self.HAS_WON_KEY: self.has_won,
            self.RELEVANCE_KEY: self.relevance,
        }

        self.__features = {}

    def __extract_place(self, raw_data: dict):
        if raw_data["scratched"]:
            return -1

        if 'finalPosition' in raw_data:
            return int(raw_data["finalPosition"])

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
    def n_past_races(self) -> int:
        return len(self.past_races)

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.__features.keys())

    @property
    def values(self) -> List:
        self.__base_attributes.update(self.__features)
        return list(self.__base_attributes.values())
