from collections import defaultdict
from datetime import datetime
from statistics import mean, median
from typing import List

import numpy as np
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceResult import RaceResult
from DataAbstraction.Present.Weather import Weather
from DataAbstraction.util.track_name_mapping import get_unique_track_name
from util.nested_dict import nested_dict
from util.text_based_functions import get_name_similarity


class RaceCard:

    RACE_NAME_KEY: str = "race_name"
    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"
    N_HORSES_KEY: str = "n_runners"
    PLACE_NUM_KEY: str = "place_num"

    base_times: defaultdict = nested_dict()
    length_modifier: defaultdict = nested_dict()
    par_momentum: defaultdict = nested_dict()
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

        self.country = event["country"]
        self.race_result = None
        raw_result = raw_race_card["result"]

        self.win_time = -1
        if "winTimeSeconds" in raw_result:
            self.win_time = raw_result["winTimeSeconds"]

        self.has_results = False

        if raw_result:
            self.has_results = True

        self.weather = None
        if "weather" in race:
            self.weather = Weather(race["weather"])

        self.__set_head_to_head_horses(race)

        self.track_name = get_unique_track_name(raw_race_card["event"]["title"])

        self.track_id = event["idTrack"]

        self.race_number = race["raceNumber"]

        distance = race["distance"]
        self.adjusted_distance = distance
        if "adjusted_distance" in race:
            self.adjusted_distance = race["adjusted_distance"]

        self.distance_category = self.get_distance_category()

        self.going = race["trackGoing"]
        self.category = race["category"]

        self.race_type = race["raceType"]
        self.race_type_detail = race["raceTypeDetail"]

        self.num_hurdles = 0
        if "num_hurdles" in race:
            self.num_hurdles = race["num_hurdles"]

        self.race_class = race["categoryLetter"]

        if self.race_class == "":
            self.race_class = "1"

        self.surface = race["trackSurface"]
        self.age_from = race["ageFrom"]
        self.age_to = race["ageTo"]
        self.purse = int(race["purse"])
        self.purse_details = race["purseDetails"]
        self.race_status = race["raceStatus"]
        self.is_open = self.race_status == "OPN"

        self.set_horses(raw_race_card["runners"]["data"])

        self.num_winners = len([runner for runner in self.runners if runner.has_won])

        self.winner_name = ""
        first_place_horse_names = [horse.name for horse in self.horses if horse.place_racebets == 1]
        if first_place_horse_names:
            self.winner_name = first_place_horse_names[0]

        self.n_horses = len(self.horses)
        self.n_finishers = len([horse for horse in self.runners if horse.place_racebets > 0])

        self.overround = sum([1 / horse.betfair_place_sp for horse in self.runners if horse.betfair_place_sp > 0])

        if self.overround > 0:
            for horse in self.horses:
                if horse.betfair_place_sp >= 1:
                    horse.sp_win_prob = (1 / horse.betfair_place_sp)
                    horse.base_attributes[Horse.REGRESSION_LABEL_KEY] = horse.sp_win_prob

        self.places_num = -1
        self.race_result: RaceResult = RaceResult(self.runners, self.places_num)
        self.set_horse_results()

        self.__base_attributes = {
            self.RACE_NAME_KEY: self.name,
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
            self.N_HORSES_KEY: self.n_horses,
            self.PLACE_NUM_KEY: self.places_num
        }

        self.set_validity()

    def set_horses(self, raw_horses: dict) -> None:
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]
        placed_horses = sorted([horse for horse in self.horses if horse.place_racebets > 0], key=lambda horse: horse.place_racebets)

        placed_horse_idx = 0
        total_horse_distance = 0
        for horse in placed_horses:
            horse.place = placed_horse_idx
            placed_horse_idx += 1
            if horse.lengths_behind >= 0:
                total_horse_distance += horse.lengths_behind
                horse.horse_distance = total_horse_distance

        self.total_horses = self.horses

        self.runners = [horse for horse in self.horses if not horse.is_scratched]

        self.n_runners = len(self.runners)
        self.places_num = 1

        if 5 <= self.n_runners <= 7:
            self.places_num = 2
        if 8 <= self.n_runners <= 15:
            self.places_num = 3
        if 16 <= self.n_runners:
            self.places_num = 4

        for horse in self.runners:
            horse.has_placed = horse.place <= self.places_num
            horse.base_attributes[Horse.HAS_PLACED_LABEL_KEY] = horse.has_placed

        # if self.remove_non_starters:
        #     self.__remove_non_starters()

    def set_horse_results(self) -> None:
        if self.race_result:
            for horse in self.horses:
                horse.set_purse(self.purse_details)

    def set_date(self, raw_race_card: dict):
        self.date_raw = raw_race_card["race"]["postTime"]
        self.datetime = datetime.fromtimestamp(self.date_raw)
        self.date = self.datetime.date()
        self.off_time = datetime.fromtimestamp(raw_race_card["race"]["offTime"])

    def to_array(self) -> ndarray:
        total_values = []
        for horse in self.horses:
            values = self.values + horse.values
            total_values.append(values)
        return total_values

    def get_horse_by_number(self, horse_number: int) -> Horse:
        horses_with_number = [horse for horse in self.horses if horse.number == horse_number]

        if not horses_with_number:
            return None

        return horses_with_number[0]

    def get_horse_by_place(self, place: int) -> Horse:
        horse_with_place = [horse for horse in self.horses if horse.place_racebets == place]

        if not horse_with_place:
            return None
        return horse_with_place[0]

    def get_horse_by_names(self, horse_name: str, jockey_name: str) -> Horse:
        horse = self.get_horse_by_horse_name(horse_name)
        if horse is None:
            horse = self.get_horse_by_jockey(jockey_name)

        return horse

    def get_horse_by_horse_name(self, horse_name: str) -> Horse:
        best_matched_horse = None
        best_common_substring_fraction = 0.5
        horse_name_a = horse_name.replace("'", "").upper().replace(" ", "").replace(".", "")

        for horse in self.horses:
            horse_name_b = horse.name.replace("'", "").upper().replace(" ", "").replace(".", "")
            common_substring_fraction = get_name_similarity(horse_name_a, horse_name_b)
            if common_substring_fraction > best_common_substring_fraction:
                best_matched_horse = horse
                best_common_substring_fraction = common_substring_fraction

        return best_matched_horse

    def get_horse_by_jockey(self, jockey_name: str) -> Horse:
        best_matched_horse = None
        best_common_substring_fraction = 0.5
        jockey_name_a = jockey_name.split(" ")[-1]

        for horse in self.horses:
            if horse.jockey.last_name:
                jockey_name_b = horse.jockey.last_name
                common_substring_fraction = get_name_similarity(jockey_name_a, jockey_name_b)
                if common_substring_fraction > best_common_substring_fraction:
                    best_matched_horse = horse
                    best_common_substring_fraction = common_substring_fraction

        return best_matched_horse

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
    def get_par_momentum_estimate(self) -> dict:
        return RaceCard.par_momentum[self.race_class][self.race_type_detail][self.num_hurdles]

    @property
    def track_variant_estimate(self) -> dict:
        if self.track_name not in RaceCard.track_variant:
            RaceCard.track_variant[self.track_name] = {"count": 0}

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
        RaceCard.track_variant = {}

    def get_distance_category(self) -> float:
        distance_increment = max(int(self.adjusted_distance / 1000) * 100, 50)
        return round(self.adjusted_distance / distance_increment) * distance_increment

    def set_validity(self) -> None:
        if self.n_horses <= 1:
            self.is_valid_sample = False
            self.feature_source_validity = False

        if self.num_winners > 1:
            self.is_valid_sample = False

        if self.country != "GB":
            self.is_valid_sample = False

        if self.overround == 0:
            self.feature_source_validity = False

        # if self.category not in ["HCP"]:
        #     self.is_valid_sample = False

        if self.n_horses > 20:
            self.is_valid_sample = False

        for runner in self.runners:
            if runner.sp_win_prob == -1:
                self.is_valid_sample = False
