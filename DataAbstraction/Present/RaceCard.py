from collections import defaultdict
from datetime import datetime
from typing import List

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
        self.temperature = -1
        self.wind_speed = -1
        self.humidity = -1
        self.weather_type = ""

        self.__extract_attributes(raw_race_card)

    def __extract_attributes(self, raw_race_card: dict):
        self.set_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]

        self.country = event["country"]
        self.race_result = None
        raw_result = raw_race_card["result"]

        self.has_results = False

        if raw_result:
            self.has_results = True

        self.track_name = get_unique_track_name(raw_race_card["event"]["title"])

        self.track_id = event["idTrack"]

        self.race_number = race["raceNumber"]
        self.race_name = race["raceTitle"]

        self.distance = race["distance"]
        self.adjusted_distance = self.distance
        if "adjusted_distance" in race:
            self.adjusted_distance = race["adjusted_distance"]

        self.num_hurdles = 0
        if "num_hurdles" in race:
            self.num_hurdles = race["num_hurdles"]

        self.going = race["trackGoing"]
        self.estimated_going = -1

        self.category = race["category"]

        self.race_type = race["raceType"]
        self.race_type_detail = race["raceTypeDetail"]

        self.purse = int(race["purse"])
        self.race_class = race["categoryLetter"]

        if self.race_class == 'A':
            self.race_class = "1"

        if self.race_class == 'B':
            self.race_class = "2"

        if self.race_class == 'C':
            self.race_class = "4"

        if not self.race_class:
            if self.purse >= 40000:
                self.race_class = "1"
            if 19000 <= self.purse <= 39999:
                self.race_class = "2"
            if 9000 <= self.purse <= 18999:
                self.race_class = "3"
            if 4500 <= self.purse <= 8999:
                self.race_class = "4"
            if 2800 <= self.purse <= 4499:
                self.race_class = "5"
            if self.purse < 2800:
                self.race_class = "6"

        self.surface = race["trackSurface"]
        self.age_from = race["ageFrom"]
        self.age_to = race["ageTo"]
        self.purse_details = race["purseDetails"]
        self.race_status = race["raceStatus"]
        self.is_open = self.race_status == "OPN"

        self.places_num = 1
        self.n_horses = 0

        self.set_horses(raw_race_card["runners"]["data"])
        finish_times = [runner.finish_time for runner in self.runners if runner.finish_time > 0]
        self.finish_time_range = -1
        self.win_time = -1
        if finish_times:
            self.win_time = min(finish_times)
            worst_time = max(finish_times)
            self.finish_time_range = worst_time - self.win_time

        self.num_winners = len([runner for runner in self.runners if runner.has_won])

        self.winner_name = ""
        first_place_horse_names = [horse.name for horse in self.horses if horse.place_racebets == 1]
        if first_place_horse_names:
            self.winner_name = first_place_horse_names[0]

        self.overround = sum([1 / horse.win_sp for horse in self.runners if horse.win_sp >= 1])

        self.set_betfair_win_sp()

        self.race_result: RaceResult = RaceResult(self.runners, self.places_num)
        self.set_horse_results()

        self.__base_attributes = {
            self.RACE_NAME_KEY: self.name,
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
            self.PLACE_NUM_KEY: self.places_num
        }

        self.set_validity()

        if self.feature_source_validity:
            self.set_place_percentile_of_runners()
            self.set_relative_distance_behind_of_runners()
            self.set_uncorrected_momentum_of_runners()

    def set_horses(self, raw_horses: dict) -> None:
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]
        self.n_horses = len(self.horses)
        self.runners = [horse for horse in self.horses if not horse.is_scratched]
        self.n_runners = len(self.runners)
        self.n_finishers = len([horse for horse in self.runners if horse.place_racebets > 0])

        for runner in self.runners:
            runner.place = self.n_runners
            runner.base_attributes[Horse.PLACE_KEY] = self.n_runners

        placed_horses = sorted([horse for horse in self.horses if horse.place_racebets > 0], key=lambda horse: horse.place_racebets)

        placed_horse_idx = 1
        total_horse_distance = 0
        for horse in placed_horses:
            horse.place = placed_horse_idx
            horse.base_attributes[Horse.PLACE_KEY] = placed_horse_idx
            placed_horse_idx += 1
            if horse.lengths_behind >= 0:
                total_horse_distance += horse.lengths_behind
                horse.horse_distance = total_horse_distance

        if 5 <= self.n_runners <= 7:
            self.places_num = 2
        if 8 <= self.n_runners <= 15:
            self.places_num = 3
        if 16 <= self.n_runners:
            if self.category == "HCP":
                self.places_num = 4
            else:
                self.places_num = 3

        # placed_horses_odds = sorted([horse for horse in self.runners if horse.place_racebets > 0],
        #                        key=lambda horse: horse.win_sp)
        # n_placed_horses = len(placed_horses_odds)
        #
        # placed_horse_idx = 1
        # for horse in placed_horses_odds:
        #     horse.ranking_label = n_placed_horses - placed_horse_idx
        #     placed_horse_idx += 1
        #
        #     if horse.ranking_label == -1:
        #         print('yellow')
        #
        #     horse.base_attributes[Horse.RANKING_LABEL_KEY] = horse.ranking_label

        for horse in self.runners:
            horse.has_placed = 1 <= horse.place <= self.places_num

            if horse.has_placed:
                horse.ranking_label = 1

            if horse.has_won:
                horse.ranking_label = 2

            horse.base_attributes[Horse.RANKING_LABEL_KEY] = horse.ranking_label

        n_placed_horses = len([horse for horse in self.runners if horse.has_placed])
        if n_placed_horses > self.places_num:
            print(f"Places num is {self.places_num} but {n_placed_horses} horses placed: {self.race_id}")
            print(f"n_finishers: {self.n_finishers}")

        # if self.remove_non_starters:
        #     self.__remove_non_starters()

    def add_weather_data(self, weather_data: dict) -> None:
        pass
        # if str(self.date) in weather_data:
        #     if self.track_name in weather_data[str(self.date)]:
        #         if str(self.race_number) in weather_data[str(self.date)][self.track_name]:
        #             self.temperature = weather_data[str(self.date)][self.track_name][str(self.race_number)]["data"][0]["temp"]
        #             self.wind_speed = weather_data[str(self.date)][self.track_name][str(self.race_number)]["data"][0][
        #                 "wind_speed"]
        #             self.humidity = weather_data[str(self.date)][self.track_name][str(self.race_number)]["data"][0][
        #                 "humidity"]
        #             self.weather_type = weather_data[str(self.date)][self.track_name][str(self.race_number)]["data"][0]["weather"][0]["main"]

    def set_betfair_win_sp(self) -> None:
        for horse in self.runners:
            if horse.win_sp >= 1:
                horse.sp_win_prob = (1 / horse.win_sp) / self.overround
                horse.base_attributes[Horse.WIN_PROB_LABEL_KEY] = horse.sp_win_prob
            else:
                print(f"Race {self.race_id} turned off")
                self.is_valid_sample = False

        placed_horses = list(reversed(sorted([horse for horse in self.runners], key=lambda horse: horse.place)))

        competitors_beaten_probability = 0.0
        for horse in placed_horses:
            horse.competitors_beaten_probability = competitors_beaten_probability
            if horse.place_racebets == -1:
                horse.competitors_beaten_probability = 0.0
            if horse.place_racebets == 1:
                horse.competitors_beaten_probability = 1.0
            competitors_beaten_probability += horse.sp_win_prob

    def set_place_percentile_of_runners(self) -> None:
        for horse in self.runners:
            if horse.place > self.n_runners:
                print(f"{horse.place}/{self.n_finishers}/{self.race_id}/{horse.name}")

            if self.n_finishers == 1:
                horse.place_percentile = 1.0
            else:
                if horse.place > 0 and len(self.runners) > 1:
                    horse.place_percentile = 1 - (horse.place - 1) / (self.n_runners - 1)

    def set_relative_distance_behind_of_runners(self) -> None:
        for horse in self.runners:
            if horse.horse_distance >= 0 and self.adjusted_distance > 0:
                if horse.place_racebets == 1:
                    second_place_horse = self.get_horse_by_place(2)
                    second_place_distance = 0
                    if second_place_horse is not None:
                        second_place_distance = second_place_horse.horse_distance

                    horse.relative_distance_behind = second_place_distance / self.adjusted_distance
                else:
                    horse.relative_distance_behind = -(horse.horse_distance / self.adjusted_distance)

    def set_momentum_of_runners(self) -> None:
        for horse in self.runners:
            if horse.uncorrected_momentum > 0:
                track_variant = 1.0
                if "value" in self.track_variant_estimate:
                    track_variant = self.track_variant_estimate["value"]

                horse.momentum = horse.uncorrected_momentum * track_variant

    def set_uncorrected_momentum_of_runners(self) -> None:
        for horse in self.runners:
            if horse.jockey.weight > 0:
                velocity = self.get_velocity(horse)
                if velocity > 0:
                    horse.uncorrected_momentum = velocity * horse.jockey.weight

    def get_velocity(self, horse: Horse) -> float:
        if self.adjusted_distance > 0:
            if horse.finish_time > 0:
                return self.adjusted_distance / horse.finish_time

            if self.win_time > 0 and horse.horse_distance >= 0:
                horse_m_behind = self.horse_lengths_behind_to_horse_m_behind(horse.horse_distance)
                total_m_run = self.adjusted_distance - horse_m_behind

                return total_m_run / self.win_time

        return -1

    def horse_lengths_behind_to_horse_m_behind(self, horse_distance: float) -> float:
        metres_per_length = 2.4
        return horse_distance * metres_per_length

    def set_horse_results(self) -> None:
        if self.race_result:
            for horse in self.horses:
                horse.set_purse(self.purse_details)

    def set_date(self, raw_race_card: dict):
        self.date_raw = raw_race_card["race"]["postTime"]
        self.datetime = datetime.fromtimestamp(self.date_raw)
        self.date = self.datetime.date()
        self.raw_off_time = raw_race_card["race"]["offTime"]
        self.off_time = datetime.fromtimestamp(self.raw_off_time)

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

    @property
    def name(self) -> str:
        return f"{self.track_name} {self.race_number}"

    @property
    def runner_ids(self):
        return [horse_id for horse_id in self.horses]

    @property
    def get_par_momentum_estimate(self) -> dict:
        return RaceCard.par_momentum[self.race_class][self.race_type_detail][self.num_hurdles][self.going]

    @property
    def track_variant_estimate(self) -> dict:
        if self.track_name not in RaceCard.track_variant:
            RaceCard.track_variant[self.track_name] = {"count": 0}

        return RaceCard.track_variant[self.track_name]

    @staticmethod
    def reset_track_variant_estimate() -> None:
        RaceCard.track_variant = {}

    def set_validity(self) -> None:
        if self.n_horses <= 1:
            self.is_valid_sample = False
            self.feature_source_validity = False

        if self.n_horses > 30:
            self.is_valid_sample = False

        if self.num_winners > 1:
            self.is_valid_sample = False

        if self.country != "GB":
            self.is_valid_sample = False
