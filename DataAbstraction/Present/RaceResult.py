from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult


class RaceResult:

    def __init__(self, runners: List[Horse], places_num: int):
        self.runner_results = {}

        for runner in runners:
            self.runner_results[runner.number] = HorseResult(
                race_name="",
                race_date_time="",
                name="",
                place=runner.place_racebets,
                win_probability=0,
                place_probability=0,
                win_odds=0,
                place_odds=0,
                place_num=0,
                has_won=runner.has_won,
                has_placed=runner.has_placed
            )

        self.places_num = places_num
        self.runner_numbers = list(self.runner_results.keys())

    def get_result_of_runner(self, runner_name: str) -> HorseResult:
        return self.runner_results[runner_name]

    def is_non_runner(self, horse_number: int):
        return horse_number not in self.runner_numbers
