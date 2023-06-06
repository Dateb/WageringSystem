from typing import Dict

import numpy as np
import pandas as pd
from numpy import ndarray
from pandas import DataFrame

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.WinBet import WinBet
from Model.Betting.BettingSlip import BettingSlip
from Model.Probabilizing.Probabilizer import Probabilizer
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_betting_slips(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> Dict[str, BettingSlip]:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)
        race_cards_dataframe["place_probability"] = "0"

        print(list(race_cards_dataframe["win_probability"]))
        return self.get_betting_slips(race_cards_dataframe)

    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        return WinBet([horse_result], stakes_fraction)

    def get_probabilities(self, betting_slip: BettingSlip) -> ndarray:
        return np.array([horse_result.win_probability for horse_result in betting_slip.horse_results])

    def get_odds(self, betting_slip: BettingSlip) -> ndarray:
        return np.array([horse_result.win_odds for horse_result in betting_slip.horse_results])
