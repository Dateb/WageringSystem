from datetime import datetime
from typing import List

import numpy as np
from numpy import ndarray

from DataAbstraction.Horse import Horse


class RaceCard:

    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.race_id = race_id

        self.__extract_attributes(raw_race_card)
        if remove_non_starters:
            self.__remove_non_starters()
        #self.__set_head_to_head_horses()

    def __extract_attributes(self, raw_race_card: dict):
        self.__extract_horses(raw_race_card["runners"]["data"])
        self.__extract_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]
        result = raw_race_card["result"]

        self.title = event["title"]
        self.number = race["raceNumber"]
        self.winner_id = str(result["positions"][0]["idRunner"])

        self.__base_attributes = {
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
        }

    def __extract_horses(self, raw_horses: dict):
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]

    def __extract_date(self, raw_race_card: dict):
        post_time = raw_race_card["race"]["postTime"]
        self.datetime = datetime.fromtimestamp(post_time)
        self.date = self.datetime.date()

    def __remove_non_starters(self):
        non_starters = [horse_id for horse_id in self.horses if self.is_horse_scratched(horse_id)]
        for non_starter in non_starters:
            del self.horses[non_starter]

    def to_array(self) -> ndarray:
        total_values = []
        for horse in self.horses:
            values = self.values + horse.values
            total_values.append(values)
        return np.asarray(total_values)

    @property
    def values(self) -> List:
        return list(self.__base_attributes.values())

    @property
    def attributes(self) -> List[str]:
        return list(self.__base_attributes.keys()) + self.horses[0].attributes

    def remove_horse(self, horse_id: str):
        del self.horses[horse_id]

    def set_odds_of_horse(self, horse_id: str, odds: float):
        self.horses[horse_id].current_odds = odds

    def get_name_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["name"]

    def is_horse_scratched(self, horse_id: str) -> bool:
        return self.horses[horse_id]["scratched"]

    def jockey_last_name_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["jockey"]["lastName"]

    def get_subject_id_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["idSubject"]

    def get_data_of_subject(self, subject_id: str) -> dict:
        for horse_id in self.horses:
            horse_data = self.horses[horse_id]
            if horse_data["idSubject"] == subject_id:
                return horse_data

    # def __set_head_to_head_horses(self):
    #     self.__head_to_head_horses = []
    #
    #     if "head2head" in self.__race:
    #         head_to_head_races = self.__race["head2head"]
    #         for head_to_head_race in head_to_head_races:
    #             self.__head_to_head_horses += head_to_head_race["runners"]

    def get_past_races_of_horse(self, horse_id: str):
        subject_id = self.get_subject_id_of_horse(horse_id)
        horse_data = self.get_data_of_subject(subject_id)
        if "pastRaces" in horse_data:
            return horse_data["pastRaces"]

        return []

    def past_speed_ratings_of_horse(self, horse_id: str, base_time: float) -> List[float]:
        past_times = self.past_times_of_horse(horse_id)
        return [
            self.__speed_rating_calculator.compute_speed_rating_from_time(self.distance, past_time)
            for past_time in past_times
        ]

    def past_times_of_horse(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        return [self.time_of_past_race(past_race) for past_race in form_table]

    def time_of_past_race(self, past_race: dict) -> float:
        if "horseDistance" in past_race and past_race["winTimeSeconds"] != -1:
            if past_race["finalPosition"] == 1:
                return past_race["winTimeSeconds"]
            else:
                return past_race["winTimeSeconds"] + (0.2 * past_race["horseDistance"])
        else:
            return -1

    def past_times_of_horse_same_track(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        past_times = self.past_times_of_horse(horse_id)
        past_times_same_track = []
        for i, past_race in enumerate(form_table):
            if past_race["trackName"] == self.title and past_times[i] != -1:
                past_times_same_track.append(past_times[i])
            else:
                past_times_same_track.append(-1)

        return past_times_same_track

    def past_speeds_of_horse(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        past_speeds = []
        for past_race in form_table:
            if "horseDistance" in past_race and past_race["raceDistance"] != 0 and past_race["winTimeSeconds"] != -1:
                race_distance = past_race["raceDistance"]
                if past_race["finalPosition"] == 1:
                    time = past_race["winTimeSeconds"]
                else:
                    time = past_race["winTimeSeconds"] + (0.2 * past_race["horseDistance"])

                speed = race_distance / time
                past_speeds.append(speed)
            else:
                past_speeds.append(-1)

        return past_speeds

    def past_speeds_of_horse_similar_distance(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        past_speeds = self.past_speeds_of_horse(horse_id)
        past_speeds_similar_distance = []
        for i, past_race in enumerate(form_table):
            distance_lower_bound = self.distance - 250
            distance_upper_bound = self.distance + 250
            if distance_lower_bound < past_race["raceDistance"] < distance_upper_bound and past_speeds[i] != -1:
                past_speeds_similar_distance.append(past_speeds[i])

        return past_speeds_similar_distance

    def past_speeds_of_horse_same_track(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        past_speeds = self.past_speeds_of_horse(horse_id)
        past_speeds_same_track = []
        for i, past_race in enumerate(form_table):
            if past_race["trackName"] == self.title and past_speeds[i] != -1:
                past_speeds_same_track.append(past_speeds[i])

        return past_speeds_same_track

    def past_speeds_of_horse_same_going(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        past_speeds = self.past_speeds_of_horse(horse_id)
        past_speeds_same_going = []
        for i, past_race in enumerate(form_table):
            if past_race["trackGoing"] == self.track_going and past_speeds[i] != -1:
                past_speeds_same_going.append(past_speeds[i])

        return past_speeds_same_going

    def horse_distances_of_horse(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        horse_distances = []
        for past_race in form_table:
            if "horseDistance" in past_race and past_race["raceDistance"] != 0:
                horse_distances.append(past_race["horseDistance"] / past_race["raceDistance"])

        return horse_distances

    def horse_rating_n_races_ago(self, horse_id: str, n_races_ago: int) -> int:
        if n_races_ago == 0:
            return self.rating_of_horse(horse_id)

        form_table = self.form_table_of_horse(horse_id)
        if n_races_ago + 1 > len(form_table) or "rating" not in form_table[n_races_ago - 1]:
            return -1

        return form_table[n_races_ago - 1]["rating"]

    def horse_predicted_place(self, horse_id: str) -> int:
        horse_odds = self.get_current_odds_of_horse(horse_id)
        odds_of_race = self.get_current_odds()

        lower_odds = [odds for odds in odds_of_race if odds < horse_odds]
        predicted_place = 1 + len(lower_odds)

        return predicted_place

    def jockey_earnings_of_horse(self, subject_id: str) -> int:
        jockey_stats = self.jockey_stats_of_horse(subject_id)
        if jockey_stats is not False:
            return jockey_stats["earnings"]
        return -1

    def jockey_wins_of_horse(self, subject_id: str) -> int:
        jockey_stats = self.jockey_stats_of_horse(subject_id)
        if jockey_stats is not False:
            return jockey_stats["numWin"]
        return -1

    def jockey_num_races_of_horse(self, subject_id: str) -> int:
        jockey_stats = self.jockey_stats_of_horse(subject_id)
        if jockey_stats is not False:
            return jockey_stats["numRaces"]
        return -1

    def jockey_stats_of_horse(self, subject_id: str) -> dict:
        horse = self.get_data_of_subject(subject_id)
        jockey = horse["jockey"]
        return jockey["stats"]

    def trainer_earnings_of_horse(self, subject_id: str) -> int:
        trainer_stats = self.trainer_stats_of_horse(subject_id)
        if trainer_stats is not False:
            return trainer_stats["earnings"]
        return -1

    def trainer_wins_of_horse(self, subject_id: str) -> int:
        trainer_stats = self.trainer_stats_of_horse(subject_id)
        if trainer_stats is not False:
            return trainer_stats["numWin"]
        return -1

    def trainer_num_races_of_horse(self, subject_id: str) -> int:
        trainer_stats = self.trainer_stats_of_horse(subject_id)
        if trainer_stats is not False:
            return trainer_stats["numRaces"]
        return -1

    def trainer_stats_of_horse(self, subject_id: str) -> dict:
        horse = self.get_data_of_subject(subject_id)
        trainer = horse["trainer"]
        return trainer["stats"]

    def rating_of_horse(self, horse_id: str) -> int:
        rating = int(float(self.horses[horse_id]["rating"]))
        if rating == 0:
            return -1
        return rating

    def post_position_of_horse(self, subject_id: str) -> int:
        horse = self.get_data_of_subject(subject_id)
        if "postPosition" in horse:
            return int(horse["postPosition"])
        return -1

    def past_ratings_of_horse(self, horse_id: str) -> List[int]:
        form_table = self.form_table_of_horse(horse_id)
        ratings = []
        for past_race in form_table:
            if "rating" in past_race:
                ratings.append(past_race["rating"])

        return ratings

    def purse_history_of_horse_and_jockey(self, horse_id: str, current_jockey_last_name: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        for past_race in form_table:
            name_split = past_race["jockey"].split()
            past_race["jockeyLastName"] = "" if len(name_split) == 0 else name_split[-1]
        past_races_of_jockey = [
            past_race for past_race in form_table if past_race["jockeyLastName"] == current_jockey_last_name
        ]

        purse_history = []
        for past_race in past_races_of_jockey:
            purse_history.append(self.purse_to_value(past_race["purse"]))

        return purse_history

    def purse_history_of_horse_by_track(self, horse: str) -> List[float]:
        purse_history = []
        track_name = self.__event["title"]
        for past_race in self.form_table_of_horse(horse):
            if past_race["trackName"] == track_name:
                purse_history.append(self.purse_to_value(past_race["purse"]))

        return purse_history

    def purse_history_of_horse(self, horse: str) -> List[float]:
        return [self.purse_to_value(past_race["purse"]) for past_race in self.form_table_of_horse(horse)]

    def purse_to_value(self, purse: str):
        purse_suffix = purse[-1]
        purse_without_suffix = purse[:-1]
        if purse_suffix == "k":
            return float(purse_without_suffix) * 1000
        elif purse_suffix == "M":
            return float(purse_without_suffix) * 1000000
        else:
            return 0.0

    def subject_to_horse_id(self, subject_id: str) -> str:
        return str(self.get_data_of_subject(subject_id)["idRunner"])

    @property
    def name(self) -> str:
        return f"{self.title} {self.number}"

    @property
    def start_time(self):
        return self.__event["firstStart"]

    @property
    def track_id(self) -> str:
        return self.__event["idTrack"]

    @property
    def category(self) -> str:
        return self.__race["category"]

    @property
    def race(self) -> dict:
        return self.__race

    @property
    def surface(self) -> str:
        return self.__race["trackSurface"]

    @property
    def distance(self) -> int:
        return self.__race["distance"]

    @property
    def n_runners(self) -> int:
        return len(self.horses)

    @property
    def runner_ids(self):
        return [horse_id for horse_id in self.horses]

    @property
    def horse_names(self) -> List[str]:
        return [self.horses[horse_id]['name'] for horse_id in self.horses]

    @property
    def head_to_head_horses(self) -> List[str]:
        return self.__head_to_head_horses

    @property
    def track_going(self) -> float:
        return self.__race["trackGoing"]

    @property
    def race_class(self) -> str:
        return self.__race["categoryLetter"]

    @property
    def subject_ids(self):
        return [self.horses[horse_id]["idSubject"] for horse_id in self.horses]

    @property
    def is_final(self):
        return self.__race["raceStatus"] == "FNL"

    @property
    def jockey_names(self) -> List[str]:
        first_names = [self.horses[horse_id]['jockey']['firstName'] for horse_id in self.horses]
        last_names = [self.horses[horse_id]['jockey']['lastName'] for horse_id in self.horses]
        return [f"{first_names[i]} {last_names[i]}" for i in range(len(first_names))]

    @property
    def trainer_names(self) -> List[str]:
        first_names = [self.horses[horse_id]['trainer']['firstName'] for horse_id in self.horses]
        last_names = [self.horses[horse_id]['trainer']['lastName'] for horse_id in self.horses]
        return [f"{first_names[i]} {last_names[i]}" for i in range(len(first_names))]
