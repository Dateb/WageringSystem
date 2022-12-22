from abc import abstractmethod, ABC
from typing import Dict, List
from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.BettingSlip import BettingSlip
from Estimators.EstimationResult import EstimationResult
import pandas as pd

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, additional_ev_threshold: float, bet_generators: List[BetGenerator]):
        self.additional_ev_threshold = additional_ev_threshold
        self.bet_generators = bet_generators

    @abstractmethod
    def bet(self, estimation_result: EstimationResult) -> Dict[str, BettingSlip]:
        pass
