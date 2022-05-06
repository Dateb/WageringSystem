from datetime import datetime
from typing import List

from DataAbstraction.FormGuideFactory import FormGuideFactory


class RaceCard:

    def __init__(self, race_id: str, raw_race: dict):
        self.__race_id = race_id
        self.__raw_race = raw_race

        self.__check_raw_data()

        self.__extract_data()
        self.__remove_non_starters()
        self.__set_head_to_head_horses()
        self.__set_form_guides()

    def __check_raw_data(self):
        if 'race' not in self.__raw_race:
            raise KeyError('Race with id {race_id} does not exist'.format(race_id=self.__race_id))

        if 'runners' not in self.__raw_race:
            raise KeyError('Runners for race with id {race_id} does not exist'.format(race_id=self.__race_id))

        if 'data' not in self.__raw_race['runners']:
            raise KeyError('Runners dict exists but does not have \'data\' key')

    def __extract_data(self):
        self.__event = self.__raw_race["event"]
        self.__race = self.__raw_race["race"]
        self.__horse_data = self.__raw_race["runners"]["data"]
        self.__result = self.__raw_race["result"]

        self.__datetime = datetime.fromtimestamp(self.__race["postTime"])

    def __remove_non_starters(self):
        non_starters = [horse_id for horse_id in self.__horse_data if self.is_horse_scratched(horse_id)]
        for non_starter in non_starters:
            del self.__horse_data[non_starter]

    def __set_form_guides(self):
        form_guide_factory = FormGuideFactory()
        self.__form_guides = {subject_id: form_guide_factory.run(subject_id) for subject_id in self.subject_ids}

    def get_name_of_horse(self, horse_id: str) -> str:
        return self.__horse_data[horse_id]["name"]

    def is_horse_scratched(self, horse_id: str) -> bool:
        return self.__horse_data[horse_id]["scratched"]

    def get_place_of_horse(self, horse_id: str) -> int:
        horse_data = self.__horse_data[horse_id]
        if horse_data["scratched"]:
            return -1

        if 'finalPosition' in horse_data:
            return int(horse_data["finalPosition"])

        return 100

    def get_current_odds_of_horse(self, horse_id: str) -> float:
        odds_of_horse = self.__horse_data[horse_id]["odds"]
        if odds_of_horse["FXW"] == 0:
            return odds_of_horse["PRC"]
        return odds_of_horse["FXW"]

    def get_subject_id_of_horse(self, horse_id: str) -> str:
        return self.__horse_data[horse_id]["idSubject"]

    def get_data_of_subject(self, subject_id: str) -> dict:
        for horse_id in self.horses:
            horse_data = self.__horse_data[horse_id]
            if horse_data["idSubject"] == subject_id:
                return horse_data

    def __set_head_to_head_horses(self):
        self.__head_to_head_horses = []

        if "head2head" in self.__race:
            head_to_head_races = self.__race["head2head"]
            for head_to_head_race in head_to_head_races:
                self.__head_to_head_horses += head_to_head_race["runners"]

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
    def race(self) -> dict:
        return self.__race

    @property
    def horses(self) -> dict:
        return self.__horse_data

    @property
    def surface(self) -> str:
        return self.__race["trackSurface"]

    @property
    def distance(self) -> int:
        return self.__race["distance"]

    @property
    def n_runners(self) -> int:
        return len(self.__horse_data)

    @property
    def runner_ids(self):
        return [horse_id for horse_id in self.__horse_data]

    @property
    def horse_names(self) -> List[str]:
        return [self.__horse_data[horse_id]['name'] for horse_id in self.__horse_data]

    @property
    def head_to_head_horses(self) -> List[str]:
        return self.__head_to_head_horses

    @property
    def track_going(self) -> float:
        return self.__race["trackGoing"]

    @property
    def subject_ids(self):
        return [self.__horse_data[horse_id]["idSubject"] for horse_id in self.__horse_data]

    @property
    def jockey_names(self) -> List[str]:
        first_names = [self.__horse_data[horse_id]['jockey']['firstName'] for horse_id in self.__horse_data]
        last_names = [self.__horse_data[horse_id]['jockey']['lastName'] for horse_id in self.__horse_data]
        return [f"{first_names[i]} {last_names[i]}" for i in range(len(first_names))]

    @property
    def trainer_names(self) -> List[str]:
        first_names = [self.__horse_data[horse_id]['trainer']['firstName'] for horse_id in self.__horse_data]
        last_names = [self.__horse_data[horse_id]['trainer']['lastName'] for horse_id in self.__horse_data]
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
    def raw_race(self) -> dict:
        return self.__raw_race

