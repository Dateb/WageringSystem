from typing import List

import numpy as np
import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor


class WinBettor(Bettor):

    def __init__(self, kelly_wealth: float):
        self.__kelly_wealth = kelly_wealth

    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        bets_df = self._add_kelly_stakes(samples)

        if bets_df.empty:
            return [Bet(race_id="0", type=BetType.WIN, stakes=0, runner_ids=[])]

        bets_df["stakes"] = bets_df["kelly_fraction"] * self.__kelly_wealth
        bets_df.loc[bets_df["stakes"] < 0.5, "stakes"] = 0.0

        return self._dataframe_to_bets(bets_df, bet_type=BetType.WIN)
