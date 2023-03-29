from abc import abstractmethod, ABC
from typing import Dict
from Model.Betting.BettingSlip import BettingSlip
import pandas as pd

from Model.Probabilizing.Probabilizer import Probabilizer

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, additional_ev_threshold: float, probabilizer: Probabilizer):
        self.ev_threshold = additional_ev_threshold
        self.probabilizer = probabilizer

    @abstractmethod
    def bet(self, betting_slips: Dict[str, BettingSlip]) -> Dict[str, BettingSlip]:
        pass
