from datetime import datetime
from typing import List


class RaceCard:

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        self.__race_id = race_id
        self.__raw_race_card = raw_race_card

        self.__check_raw_data()

        self.__extract_data()
        if remove_non_starters:
            self.__remove_non_starters()
        self.__set_head_to_head_horses()

    def __check_raw_data(self):
        if 'race' not in self.__raw_race_card:
            raise KeyError('Race with id {race_id} does not exist'.format(race_id=self.__race_id))

        if 'runners' not in self.__raw_race_card:
            raise KeyError('Runners for race with id {race_id} does not exist'.format(race_id=self.__race_id))

        if 'data' not in self.__raw_race_card['runners']:
            raise KeyError('Runners dict exists but does not have \'data\' key')

    def __extract_data(self):
        self.__event = self.__raw_race_card["event"]
        self.__race = self.__raw_race_card["race"]
        self.horses = self.__raw_race_card["runners"]["data"]
        self.__result = self.__raw_race_card["result"]

        self.__datetime = datetime.fromtimestamp(self.__race["postTime"])

    def __remove_non_starters(self):
        non_starters = [horse_id for horse_id in self.horses if self.is_horse_scratched(horse_id)]
        for non_starter in non_starters:
            del self.horses[non_starter]

    def remove_horse(self, horse_id: str):
        del self.horses[horse_id]

    def set_odds_of_horse(self, horse_id: str, odds: float):
        self.horses[horse_id]["odds"]["FXW"] = odds

    def get_name_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["name"]

    def is_horse_scratched(self, horse_id: str) -> bool:
        return self.horses[horse_id]["scratched"]

    def get_place_of_horse(self, horse_id: str) -> int:
        horse_data = self.horses[horse_id]
        if horse_data["scratched"]:
            return -1

        if 'finalPosition' in horse_data:
            return int(horse_data["finalPosition"])

        return 100

    def jockey_last_name_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["jockey"]["lastName"]

    def get_current_odds(self):
        return [self.get_current_odds_of_horse(horse) for horse in self.horses]

    def get_current_odds_of_horse(self, horse_id: str) -> float:
        odds_of_horse = self.horses[horse_id]["odds"]
        if odds_of_horse["FXW"] == 0:
            return odds_of_horse["PRC"]
        return odds_of_horse["FXW"]

    def get_subject_id_of_horse(self, horse_id: str) -> str:
        return self.horses[horse_id]["idSubject"]

    def get_data_of_subject(self, subject_id: str) -> dict:
        for horse_id in self.horses:
            horse_data = self.horses[horse_id]
            if horse_data["idSubject"] == subject_id:
                return horse_data

    def __set_head_to_head_horses(self):
        self.__head_to_head_horses = []

        if "head2head" in self.__race:
            head_to_head_races = self.__race["head2head"]
            for head_to_head_race in head_to_head_races:
                self.__head_to_head_horses += head_to_head_race["runners"]

    def get_past_races_of_horse(self, horse_id: str):
        subject_id = self.get_subject_id_of_horse(horse_id)
        horse_data = self.get_data_of_subject(subject_id)
        if "pastRaces" in horse_data:
            return horse_data["pastRaces"]

        return []

    def form_table_of_horse(self, horse_id: str) -> List[dict]:
        return self.horses[horse_id]["formTable"]

    def horse_distances_of_horse(self, horse_id: str) -> List[float]:
        form_table = self.form_table_of_horse(horse_id)
        horse_distances = []
        for past_race in form_table:
            if "horseDistance" in past_race:
                horse_distances.append(past_race["horseDistance"])

        return horse_distances

    def rating_of_horse(self, horse_id: str) -> int:
        return self.horses[horse_id]["rating"]

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

    def purse_to_value(self, purse: str):
        purse_suffix = purse[-1]
        purse_without_suffix = purse[:-1]
        if purse_suffix == "k":
            return float(purse_without_suffix) * 1000
        elif purse_suffix == "M":
            return float(purse_without_suffix) * 1000000
        else:
            return 0.0

    @property
    def name(self) -> str:
        return f"{self.title} {self.number}"

    @property
    def title(self) -> str:
        return self.__event["title"]

    @property
    def number(self) -> str:
        return self.__race["raceNumber"]

    @property
    def datetime(self):
        return self.__datetime

    @property
    def date(self):
        return self.__datetime.date()

    @property
    def start_time(self):
        return self.__event["firstStart"]

    @property
    def race_id(self) -> str:
        return self.__race_id

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

    @property
    def exacta_odds(self) -> float:
        if "other" in self.__result["odds"]:
            return float(list(self.__result["odds"]["other"][0]["EXA"].keys())[0])

        return 0.0

    @property
    def trifecta_odds(self) -> float:
        if "other" in self.__result["odds"]:
            if len(self.__result["odds"]["other"]) > 1:
                if "TRI" in self.__result["odds"]["other"][1]:
                    return float(list(self.__result["odds"]["other"][1]["TRI"].keys())[0])

        return 0.0

    @property
    def raw_race_card(self) -> dict:
        return self.__raw_race_card
