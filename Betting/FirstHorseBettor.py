from typing import Dict

import pandas as pd

from Betting.BettingSlip import BetType, BettingSlip
from Betting.Bettor import Bettor
from DataAbstraction.Present.Horse import Horse


class FirstHorseBettor(Bettor):

    def __init__(self, kelly_wealth: float):
        super().__init__(kelly_wealth)

    def _get_bet_of_first_horse_per_race(self, samples: pd.DataFrame):
        return samples.groupby(Horse.RACE_ID_KEY).head(1)

    def bet(self, race_cards_sample: pd.DataFrame) -> Dict[str, BettingSlip]:
        bets_df = self._get_bet_of_first_horse_per_race(race_cards_sample)
        bets_df["stakes"] = self._kelly_wealth * 0.5

        print(bets_df)
        return self._dataframe_to_betting_slips(bets_df, bet_type=BetType.WIN)

