import numpy as np
import pandas as pd
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.WinBet import WinBet
from Model.Estimation.RaceEventProbabilities import RaceEventProbabilities
from Model.Probabilizing.Probabilizer import Probabilizer
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_event_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceEventProbabilities:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)
        race_cards_dataframe["place_probability"] = "0"

        race_cards_dataframe["expected_value"] = race_cards_dataframe[Horse.WIN_PROBABILITY_KEY] \
                                                 * race_cards_dataframe[Horse.CURRENT_WIN_ODDS_KEY] \
                                                 * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)

        return RaceEventProbabilities(race_cards_dataframe)

    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        return WinBet([horse_result], stakes_fraction)
