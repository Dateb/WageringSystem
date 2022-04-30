from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor


class FavoriteBettor(Bettor):

    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        bets_df = self._get_lowest_n_odds(samples, 1)
        bets_df["stakes"] = 1.0

        return self._dataframe_to_bets(bets_df, bet_type=BetType.WIN)

