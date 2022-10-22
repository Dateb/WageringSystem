from abc import ABC, abstractmethod
from typing import List

from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class Bet(ABC):

    BET_TAX: float = 0.05

    def __init__(self, predicted_horse_results: List[HorseResult], stakes_fraction: float, success_probability: float):
        self.predicted_horse_results = predicted_horse_results
        self.stakes_fraction = stakes_fraction
        self.success_probability = success_probability

        self.potential_win = 0
        self.win = 0
        self.loss = stakes_fraction * (1 + self.BET_TAX)
        self.odds = 0

    @abstractmethod
    def is_won(self, race_result: RaceResult) -> bool:
        pass
