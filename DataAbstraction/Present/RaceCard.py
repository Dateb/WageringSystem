from collections import defaultdict
from datetime import datetime
from statistics import mean, median
from typing import List

import numpy as np
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceResult import RaceResult
from DataAbstraction.Present.Weather import Weather
from DataAbstraction.relevance_calculators import get_winner_relevance
from DataAbstraction.util.track_name_mapping import get_unique_track_name
from ModelTuning.simulate_conf import MAX_HORSES_PER_RACE
from util.nested_dict import nested_dict
from util.speed_calculator import compute_speed_figure


class RaceCard:

    RACE_NAME_KEY: str = "race_name"
    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"
    N_HORSES_KEY: str = "n_runners"
    PLACE_NUM_KEY: str = "place_num"

    base_times: defaultdict = nested_dict()
    length_modifier: defaultdict = nested_dict()
    par_time: defaultdict = nested_dict()
    track_variant: defaultdict = nested_dict()

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.is_valid_sample = True
        self.feature_source_validity = True
        self.race_id = race_id
        self.remove_non_starters = remove_non_starters

        self.__extract_attributes(raw_race_card)

    def __extract_attributes(self, raw_race_card: dict):
        self.set_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]

        self.race_result = None
        raw_result = raw_race_card["result"]
        self.has_results = False

        if raw_result:
            self.has_results = True
            self.race_result: RaceResult = RaceResult(raw_result)

        self.weather = None
        if "weather" in race:
            self.weather = Weather(race["weather"])

        self.__set_head_to_head_horses(race)

        self.track_name = get_unique_track_name(raw_race_card["event"]["title"])

        self.track_id = event["idTrack"]

        self.race_number = race["raceNumber"]
        self.distance = race["distance"]

        self.distance_category = self.get_distance_category()

        self.going = race["trackGoing"]
        self.category = race["category"]

        self.race_type = race["raceType"]
        self.race_type_detail = race["raceTypeDetail"]

        self.race_class = race["categoryLetter"]

        if self.race_class == "":
            self.race_class = "1"

        self.surface = race["trackSurface"]
        self.age_from = race["ageFrom"]
        self.age_to = race["ageTo"]
        self.purse = race["purseDetails"]
        self.is_open = race["raceStatus"] == "OPN"

        self.set_horses(raw_race_card["runners"]["data"])

        self.winner_name = [horse.name for horse in self.horses if horse.place == 1][0]

        self.n_horses = len(self.horses)

        self.set_horse_results()

        self.__base_attributes = {
            self.RACE_NAME_KEY: self.name,
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
            self.N_HORSES_KEY: self.n_horses,
        }

        self.set_validity()

        if self.feature_source_validity:
            self.overround = sum([1 / horse.racebets_win_sp for horse in self.runners])

        # TODO: there some border cases here. Would need a fix.
        # for horse in self.horses:
        #     if horse.n_past_races >= 1:
        #         previous_race_ids = [past_form.race_id for past_form in horse.form_table.past_forms]
        #
        #         if self.race_id in previous_race_ids:
        #             print(f"1 Same race id {self.race_id} for horse: {horse.name}\n")
        #
        #         if len(previous_race_ids) != len(set(previous_race_ids)):
        #             print(f"Past form of {horse.name} in race {self.race_id} contains duplicate races")

    def set_horses(self, raw_horses: dict) -> None:
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]

        self.total_horses = self.horses

        self.horses = [horse for horse in self.horses if not horse.is_scratched]
        self.runners = [horse for horse in self.horses if not horse.is_scratched]

        # if self.remove_non_starters:
        #     self.__remove_non_starters()

    def set_horse_results(self) -> None:
        if self.race_result:
            for horse in self.horses:
                horse.set_purse(self.purse)

    def set_date(self, raw_race_card: dict):
        self.date_raw = raw_race_card["race"]["postTime"]
        self.datetime = datetime.fromtimestamp(self.date_raw)
        self.date = self.datetime.date()

    def __remove_non_starters(self):
        self.horses = [horse for horse in self.horses if not horse.is_scratched]

    def to_array(self) -> ndarray:
        total_values = []
        for horse in self.horses:
            values = self.values + horse.values
            total_values.append(values)
        return total_values

    def get_horse_by_number(self, horse_number: int) -> Horse:
        horse_with_number = [horse for horse in self.horses if horse.number == horse_number][0]
        return horse_with_number

    @property
    def values(self) -> List:
        return list(self.__base_attributes.values())

    @property
    def attributes(self) -> List[str]:
        return list(self.__base_attributes.keys()) + self.horses[0].attributes

    def __set_head_to_head_horses(self, race: dict):
        self.__head_to_head_horses = []

        if "head2head" in race:
            head_to_head_races = race["head2head"]
            for head_to_head_race in head_to_head_races:
                self.__head_to_head_horses += head_to_head_race["runners"]

    @property
    def name(self) -> str:
        return f"{self.track_name} {self.race_number}"

    @property
    def runner_ids(self):
        return [horse_id for horse_id in self.horses]

    @property
    def head_to_head_horses(self) -> List[str]:
        return self.__head_to_head_horses

    def get_base_time_estimate(self, horse_number: int) -> dict:
        # horse_weight = self.get_horse_by_number(horse_number).jockey.weight
        # weight_category = round(horse_weight / 4) * 4

        return RaceCard.base_times[self.distance_category][self.race_type_detail][self.track_id]

    @property
    def lengths_per_second_estimate(self) -> dict:
        return RaceCard.length_modifier[self.distance_category][self.race_type_detail]

    @property
    def get_par_time_estimate(self) -> dict:
        return RaceCard.par_time[self.distance_category][self.race_class][self.race_type_detail]

    @property
    def track_variant_estimate(self) -> dict:
        return RaceCard.track_variant[self.track_name]

    @property
    def favorite(self) -> Horse:
        min_odds = np.inf
        favorite = None
        for horse in self.horses:
            if horse.betfair_win_sp < min_odds:
                min_odds = horse.betfair_win_sp
                favorite = horse

        return favorite

    @property
    def has_foreigners(self) -> bool:
        foreigners = [1 for horse in self.horses if horse.homeland not in ["GB", None]]
        return len(foreigners) > 0

    @property
    def json(self) -> dict:
        return {
            "name": self.name
        }

    @staticmethod
    def reset_track_variant_estimate() -> None:
        RaceCard.track_variant = nested_dict()

    def get_distance_category(self) -> float:
        distance_increment = max(int(self.distance / 1000) * 100, 50)
        return round(self.distance / distance_increment) * distance_increment

    def set_validity(self) -> None:
        if self.n_horses <= 1:
            self.is_valid_sample = False
            self.feature_source_validity = False

        if self.category not in ["LST", "HCP"]:
            self.is_valid_sample = False

        if self.n_horses > MAX_HORSES_PER_RACE:
            self.is_valid_sample = False

        # for horse in self.horses:
        #     if not horse.form_table.past_forms:
        #         self.is_valid_sample = False
