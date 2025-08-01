from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import List

import numpy as np
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceResult import RaceResult
from DataAbstraction.Present.Weather import Weather
from DataAbstraction.util.track_name_mapping import get_unique_track_name
from util.nested_dict import nested_dict


class RaceCard:

    RACE_NAME_KEY: str = "race_name"
    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"
    N_HORSES_KEY: str = "n_runners"
    PLACE_NUM_KEY: str = "place_num"

    BASE_ATTRIBUTE_NAMES = [RACE_NAME_KEY, DATETIME_KEY, RACE_ID_KEY, N_HORSES_KEY, PLACE_NUM_KEY]

    base_times: defaultdict = nested_dict()
    length_modifier: defaultdict = nested_dict()
    par_time: defaultdict = nested_dict()
    track_variant: defaultdict = nested_dict()

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.max_horse_padding_size = 30
        self.sample_validity = True
        self.feature_source_validity = True
        self.race_id = race_id
        self.remove_non_starters = remove_non_starters

        self.__extract_attributes(raw_race_card)

    def __extract_attributes(self, raw_race_card: dict):
        self.set_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]

        self.country = event["country"]

        self.winner_id = -1
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
        self.purse = race["purseDetails"]
        self.is_open = race["raceStatus"] == "OPN"

        self.set_horses(raw_race_card["runners"]["data"])

        if self.remove_non_starters:
            self.__remove_non_starters()

        self.n_horses = len(self.horses)

        self.mean_horse_weight = mean([horse.jockey.weight for horse in self.horses if horse.jockey.weight > 0])
        self.weight_category = round(self.mean_horse_weight / 4) * 4

        self.set_horse_results()

        self.places_num = 1
        if 5 <= self.n_horses <= 7:
            self.places_num = 2
        if 8 <= self.n_horses:
            self.places_num = 3
        if 16 <= self.n_horses and self.category == "HCP":
            self.places_num = 4

        self.__base_attributes = {
            self.RACE_NAME_KEY: self.name,
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
            self.N_HORSES_KEY: self.n_horses,
            self.PLACE_NUM_KEY: self.places_num,
        }

        self.set_validity()

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

    def get_horse_by_id(self, horse_id: str) -> Horse:
        horse_with_id = [horse for horse in self.horses if horse.horse_id == horse_id][0]
        return horse_with_id

    def get_horse_by_number(self, horse_number: int) -> Horse:
        horse_with_number = [horse for horse in self.horses if horse.number == horse_number][0]
        return horse_with_number

    @property
    def values(self) -> List:
        return list(self.__base_attributes.values())

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

    def get_base_time_estimate_of_horse(self, horse: Horse) -> dict:
        return RaceCard.base_times[self.distance_category][self.race_type_detail][self.track_id][horse.weight_category]

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
        if len(self.horses) <= 1:
            self.sample_validity = False
            self.feature_source_validity = False

        #TODO: Not a bad idea, but we should look in the form table to determine foreigners

        # if self.has_foreigners:
        #     self.sample_validity = False

        for horse in self.horses:
            if horse.betfair_place_sp == 0:
                self.sample_validity = False

    def insert_market_odds(self, market_odds: ndarray):
        for i in range(len(market_odds)):
            self.horses[i].shifted_odds = market_odds[i]

