from abc import abstractmethod, ABC
from typing import Dict

from Betting.BettingSlip import BettingSlip
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetGenerator(ABC):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        self.additional_ev_threshold = additional_ev_threshold
        self.bet_limit = bet_limit

    @abstractmethod
    def add_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        pass
