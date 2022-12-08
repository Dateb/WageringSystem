from collections import defaultdict
from datetime import datetime
from typing import List

from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceResult import RaceResult
from util.nested_dict import nested_dict
from util.speed_calculator import compute_speed_figure


class RaceCard:

    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"
    N_HORSES_KEY: str = "n_runners"
    PLACE_NUM_KEY: str = "place_num"

    base_times: defaultdict = nested_dict()
    length_modifier: defaultdict = nested_dict()
    par_time: defaultdict = nested_dict()
    track_variant: defaultdict = nested_dict()

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.race_id = race_id
        self.remove_non_starters = remove_non_starters

        self.__extract_attributes(raw_race_card)

    def __extract_attributes(self, raw_race_card: dict):
        self.set_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]

        self.winner_id = -1
        self.race_result = None
        raw_result = raw_race_card["result"]
        self.has_results = False
        if raw_result:
            self.has_results = True
            self.race_result: RaceResult = RaceResult(raw_result)

        self.__set_head_to_head_horses(race)
        self.track_name = event["title"]
        self.track_id = event["idTrack"]
        if "placesNum" not in race:
            self.place_num = 1
        else:
            self.place_num = race["placesNum"]
        self.race_number = race["raceNumber"]
        self.distance = race["distance"]
        self.going = race["trackGoing"]
        self.category = race["category"]
        self.race_type = race["raceType"]
        self.race_type_detail = race["raceTypeDetail"]
        self.race_class = race["categoryLetter"]
        self.surface = race["trackSurface"]
        self.age_from = race["ageFrom"]
        self.age_to = race["ageTo"]
        self.purse = race["purseDetails"]

        self.set_horses(raw_race_card["runners"]["data"])
        if self.remove_non_starters:
            self.__remove_non_starters()

        self.total_inverse_win_odds = 0
        for horse in self.horses:
            self.total_inverse_win_odds += horse.inverse_win_odds

        self.n_horses = len(self.horses)

        self.__base_attributes = {
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
            self.N_HORSES_KEY: self.n_horses,
            self.PLACE_NUM_KEY: self.place_num,
        }

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

    def set_horses(self, raw_horses: dict):
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]
        if self.race_result:
            for horse in self.horses:
                horse.set_purse(self.purse)

    def set_horse_relevance(self):
        if self.race_result:
            for horse in self.horses:
                speed_figure = compute_speed_figure(
                    self.base_time_estimate["avg"],
                    self.base_time_estimate["std"],
                    self.length_modifier_estimate["avg"],
                    self.estimated_base_length_modifier,
                    self.race_result.win_time,
                    horse.horse_distance,
                    self.track_variant_estimate["avg"],
                )
                horse.set_relevance(speed_figure)

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

    def get_horse_by_id(self, horse_id: str) -> Horse:
        horse_with_id = [horse for horse in self.horses if horse.horse_id == horse_id][0]
        return horse_with_id

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

    @property
    def base_time_estimate(self) -> dict:
        return RaceCard.base_times[self.distance][self.race_type_detail]

    @property
    def length_modifier_estimate(self) -> dict:
        return RaceCard.length_modifier[self.track_name][self.distance][self.surface][self.going][self.race_type_detail]

    @property
    def par_time_estimate(self) -> dict:
        return RaceCard.par_time[self.distance][self.race_class][self.race_type_detail]

    @property
    def estimated_base_length_modifier(self) -> float:
        return RaceCard.length_modifier["Wolverhampton"]["1437"]["EQT"]["0"]["FLT"]

    @property
    def track_variant_estimate(self) -> dict:
        return RaceCard.track_variant[self.track_name]
