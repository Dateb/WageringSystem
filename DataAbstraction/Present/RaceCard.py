from datetime import datetime
from typing import List

from numpy import ndarray

from DataAbstraction.Present.Horse import Horse


class RaceCard:

    DATETIME_KEY: str = "date_time"
    RACE_ID_KEY: str = "race_id"

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.race_id = race_id

        self.__extract_attributes(raw_race_card)
        if remove_non_starters:
            self.__remove_non_starters()

    def __extract_attributes(self, raw_race_card: dict):
        self.__extract_horses(raw_race_card["runners"]["data"])
        self.__extract_date(raw_race_card)

        event = raw_race_card["event"]
        race = raw_race_card["race"]
        result = raw_race_card["result"]

        self.__set_head_to_head_horses(race)
        self.track_name = event["title"]
        self.track_id = event["idTrack"]
        self.number = race["raceNumber"]
        self.distance = race["distance"]
        self.category = race["category"]
        self.surface = race["trackSurface"]
        self.winner_id = -1
        if result:
            self.winner_id = str(result["positions"][0]["idRunner"])

        self.__base_attributes = {
            self.DATETIME_KEY: self.datetime,
            self.RACE_ID_KEY: self.race_id,
        }

        # TODO: check has seemingly false positives. Increase accuracy of check.
        for horse in self.horses:
            if horse.n_past_races > 0:
                if self.date_raw == horse.past_races[0].date_raw:
                    print(self.race_id)
                    print(horse.name)
                    print(f"Same date: {self.date}")
                    print("--------------------")

    def __extract_horses(self, raw_horses: dict):
        self.horses: List[Horse] = [Horse(raw_horses[horse_id]) for horse_id in raw_horses]

    def __extract_date(self, raw_race_card: dict):
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

    def get_horse_with_id(self, horse_id: str) -> Horse:
        horse_with_id = [horse for horse in self.horses if horse.horse_id == horse_id][0]
        return horse_with_id

    @property
    def values(self) -> List:
        return list(self.__base_attributes.values())

    @property
    def attributes(self) -> List[str]:
        return list(self.__base_attributes.keys()) + self.horses[0].attributes

    def set_odds_of_horse(self, horse_id: str, odds: float):
        self.horses[horse_id].current_odds = odds

    def __set_head_to_head_horses(self, race: dict):
        self.__head_to_head_horses = []

        if "head2head" in race:
            head_to_head_races = race["head2head"]
            for head_to_head_race in head_to_head_races:
                self.__head_to_head_horses += head_to_head_race["runners"]

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

    def subject_to_horse_id(self, subject_id: str) -> str:
        return str(self.get_data_of_subject(subject_id)["idRunner"])

    @property
    def name(self) -> str:
        return f"{self.track_name} {self.number}"

    @property
    def start_time(self):
        return self.__event["firstStart"]

    @property
    def race(self) -> dict:
        return self.__race

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
