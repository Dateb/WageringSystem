from abc import abstractmethod

from numpy import ndarray

from DataAbstraction.Present.HorseResult import HorseResult
from Model.Betting.Bets.Bet import Bet
from Model.Estimation.RaceEventProbabilities import RaceEventProbabilities
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Probabilizer:

    def __init__(self):
        pass

    @abstractmethod
    def create_event_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceEventProbabilities:
        pass

    @abstractmethod
    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        pass

