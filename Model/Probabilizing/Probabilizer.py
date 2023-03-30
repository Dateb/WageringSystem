from abc import abstractmethod, ABC
from typing import Dict

import numpy as np
import pandas as pd
from numpy import ndarray
from pandas import DataFrame

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Betting.BettingSlip import BettingSlip
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Probabilizer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def create_betting_slips(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> Dict[str, BettingSlip]:
        pass

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame, scores: ndarray) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return race_cards_dataframe

    def get_betting_slips(self, race_cards_dataframe: DataFrame) -> Dict[str, BettingSlip]:
        self.race_keys = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        self.race_ids = list(race_cards_dataframe[RaceCard.RACE_ID_KEY])

        race_names = race_cards_dataframe[RaceCard.RACE_NAME_KEY].values
        race_date_times = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        horse_names = race_cards_dataframe.loc[:, Horse.NAME_KEY].values
        horse_numbers = race_cards_dataframe.loc[:, Horse.NUMBER_KEY].values

        win_odds = race_cards_dataframe.loc[:, Horse.CURRENT_WIN_ODDS_KEY].values
        place_odds = race_cards_dataframe.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values

        win_probabilities = race_cards_dataframe.loc[:, Horse.WIN_PROBABILITY_KEY].values
        place_probabilities = race_cards_dataframe.loc[:, "place_probability"].values

        place_nums = race_cards_dataframe.loc[:, RaceCard.PLACE_NUM_KEY].values

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
                    win_odds=win_odds[i],
                    place_odds=place_odds[i],
                    place_num=place_nums[i],
                )

            betting_slip.add_horse_result(horse_result)

        return betting_slips

    @abstractmethod
    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        pass

    @abstractmethod
    def get_probabilities(self, betting_slip: BettingSlip) -> ndarray:
        pass

    @abstractmethod
    def get_odds(self, betting_slip: BettingSlip) -> ndarray:
        pass

