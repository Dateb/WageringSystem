from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor


class WinBettor(Bettor):

    def __init__(self, kelly_wealth: float):
        self.__kelly_wealth = kelly_wealth

    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        samples = self._add_kelly_stakes(samples)
        bets_df = self._get_highest_n_expected_values(samples, 1)

        if bets_df.empty:
            return [Bet(race_id="0", type=BetType.WIN, stakes=0, runner_ids=[])]

        bets_df["stakes"] = bets_df["kelly_fraction"] * self.__kelly_wealth

        return self._dataframe_to_bets(bets_df, bet_type=BetType.WIN)
