from typing import List


class FormGuide:
    def __init__(self, race_id: str, subject_id: str, raw_formguide: dict):
        self.__subject_id = subject_id

        self.__raw_formguide = raw_formguide

        self.__past_races = {}

        form_table = raw_formguide["formTable"]
        self.__n_past_races = len(form_table)

        for i, past_race in enumerate(form_table):
            race_id = past_race["idRace"]
            self.__past_races[race_id] = {"country": past_race["country"]}

    @property
    def subject_id(self):
        return self.__subject_id

    @property
    def raw_formguide(self) -> dict:
        return self.__raw_formguide

    @property
    def past_race_ids(self) -> List[str]:
        return [past_race_id for past_race_id in self.__past_races]

    @property
    def gb_past_race_ids(self) -> List[str]:
        return [past_race_id for past_race_id in self.__past_races
                if self.__past_races[past_race_id]["country"] == "GB"]
