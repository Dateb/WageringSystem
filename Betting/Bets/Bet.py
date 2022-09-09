from abc import ABC, abstractmethod

from DataAbstraction.Present.RaceResult import RaceResult


class Bet(ABC):

    TAX: float = 0.05

    def __init__(self, horse_id: str, odds: float, stakes: float, stakes_fraction: float):
        self.horse_id = horse_id
        self.odds = odds
        self.stakes_fraction = stakes_fraction
        self.stakes = stakes

        self.loss = stakes * (1 + self.TAX)
        self.potential_win = odds * stakes

    @abstractmethod
    def is_won(self, race_result: RaceResult) -> bool:
        pass
