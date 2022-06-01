from typing import Dict

import pandas as pd

from Betting.BettingSlip import BettingSlip, BetType
from Betting.Bettor import Bettor


class StaticKellyBettor(Bettor):

    def __init__(self, start_kelly_wealth: float):
        super().__init__(start_kelly_wealth)

    def bet(self, samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        bets_df = self._add_stakes_fraction(samples)

        if bets_df.empty:
            return {}

        bets_df["stakes"] = bets_df["stakes_fraction"] * self._start_kelly_wealth
        bets_df.loc[bets_df["stakes"] < 0.5, "stakes"] = 0.0

        return self._dataframe_to_betting_slips(bets_df, bet_type=BetType.WIN)
