from abc import abstractmethod, ABC
from typing import Dict

from Betting.BettingSlip import BettingSlip
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetGenerator(ABC):

    def __init__(self, additional_ev_threshold: float):
        self.additional_ev_threshold = additional_ev_threshold

    @abstractmethod
    def add_single_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        pass

    @abstractmethod
    def add_multiple_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        pass
