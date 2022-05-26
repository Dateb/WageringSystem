from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor


class ExactaBettor(Bettor):

    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        bets_df = self._get_highest_n_scores(samples, 2)

        return self._dataframe_to_betting_slips(bets_df, bet_type=BetType.EXACTA)

    