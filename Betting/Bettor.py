from abc import abstractmethod, ABC
from typing import Dict, List
from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.BettingSlip import BettingSlip
from SampleExtraction.RaceCardsSample import RaceCardsSample
import pandas as pd

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, bet_generators: List[BetGenerator]):
        self.bet_generators = bet_generators

    @abstractmethod
    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        pass
