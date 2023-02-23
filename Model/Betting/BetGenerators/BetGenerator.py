from abc import abstractmethod, ABC
from typing import Dict, List

from Model.Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.HorseResult import HorseResult


class BetGenerator(ABC):

    def __init__(self, additional_ev_threshold: float, lower_win_prob_threshold: float, upper_win_prob_threshold: float):
        self.additional_ev_threshold = additional_ev_threshold
        self.lower_win_prob_threshold = lower_win_prob_threshold
        self.upper_win_prob_threshold = upper_win_prob_threshold

    @abstractmethod
    def add_bets(self, horse_results: List[HorseResult], betting_slips: Dict[str, BettingSlip]) -> None:
        pass
