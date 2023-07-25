from datetime import datetime
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
from market_simulation.odds_history import EstimationResult, create_race_key


class WinProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_estimation_result(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> EstimationResult:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)

        #TODO: fetch races from dataframe to create the estimates dynamically
        probability_estimates = {}

        for row in race_cards_dataframe.itertuples(index=False):
            race_datetime = row.date_time - pd.Timedelta(hours=2)
            track_name = row.race_name[:-2]

            race_key = create_race_key(race_datetime, track_name)

            horse_name = row.name.replace("'", "").upper()
            win_probability = row.win_probability

            if race_key not in probability_estimates:
                probability_estimates[race_key] = {}

            probability_estimates[race_key][horse_name] = win_probability

        if "2023-04-01 16:30:00_Chelmsford City" in probability_estimates:
            print("worked out")

        return EstimationResult(probability_estimates)

    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        return WinBet([horse_result], stakes_fraction)

    def get_probabilities(self, betting_slip: BettingSlip) -> ndarray:
        return np.array([horse_result.win_probability for horse_result in betting_slip.horse_results])

    def get_odds(self, betting_slip: BettingSlip) -> ndarray:
        return np.array([horse_result.win_odds for horse_result in betting_slip.horse_results])
