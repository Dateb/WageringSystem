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

        race_cards_dataframe["expected_value"] = race_cards_dataframe[Horse.WIN_PROBABILITY_KEY] \
                                                 * race_cards_dataframe[Horse.CURRENT_BETTING_ODDS_KEY] \
                                                 * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)

        return self.get_betting_slips(race_cards_dataframe, Horse.CURRENT_BETTING_ODDS_KEY)

    def get_betting_slips(self, race_cards_dataframe: DataFrame, betting_odds_key: str) -> Dict[str, BettingSlip]:
        self.race_keys = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        self.race_ids = list(race_cards_dataframe[RaceCard.RACE_ID_KEY])

        race_names = race_cards_dataframe[RaceCard.RACE_NAME_KEY].values
        race_date_times = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        horse_names = race_cards_dataframe.loc[:, Horse.NAME_KEY].values
        horse_numbers = race_cards_dataframe.loc[:, Horse.NUMBER_KEY].values

        betting_odds = race_cards_dataframe.loc[:, betting_odds_key].values
        place_odds = race_cards_dataframe.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values

        win_probabilities = race_cards_dataframe.loc[:, Horse.WIN_PROBABILITY_KEY].values
        place_probabilities = race_cards_dataframe.loc[:, "place_probability"].values

        place_nums = race_cards_dataframe.loc[:, RaceCard.PLACE_NUM_KEY].values

        expected_values = race_cards_dataframe.loc[:, "expected_value"].values

        betting_slips = {}
        for i in range(len(horse_numbers)):
            if race_date_times[i] not in betting_slips:
                betting_slips[race_date_times[i]] = BettingSlip(self.race_ids[i])

            betting_slip = betting_slips[race_date_times[i]]

            horse_result = HorseResult(
                    race_name=race_names[i],
                    race_date_time=race_date_times[i],
                    number=horse_numbers[i],
                    name=horse_names[i],
                    position=1,
                    win_probability=win_probabilities[i],
                    place_probability=place_probabilities[i],
                    betting_odds=betting_odds[i],
                    place_odds=place_odds[i],
                    place_num=place_nums[i],
                    expected_value=expected_values[i]
                )

            betting_slip.add_horse_result(horse_result)

        return betting_slips

    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        return WinBet([horse_result], stakes_fraction)
