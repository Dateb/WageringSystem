from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult


class RaceResult:

    def __init__(self, horses: List[Horse], places_num: int):
        self.horse_results = {}

        for horse in horses:
            self.horse_results[horse.name.replace("'", "").upper()] = HorseResult(
                race_name="",
                race_date_time="",
                name="",
                place=horse.place,
                win_probability=0,
                place_probability=0,
                win_odds=0,
                place_odds=0,
                place_num=0,
            )

        self.places_num = places_num

    def get_place_of_horse_name(self, horse_name: str) -> int:
        return self.horse_results[horse_name].place

    @property
    def horse_names(self) -> List[str]:
        return list(self.horse_results.keys())
