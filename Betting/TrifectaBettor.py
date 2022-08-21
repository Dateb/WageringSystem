from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor


class TrifectaBettor(Bettor):

    def bet(self, race_cards_sample: pd.DataFrame) -> List[Bet]:
        bets_df = self._get_highest_n_scores(race_cards_sample, 3)

        return self._dataframe_to_betting_slips(bets_df, bet_type=BetType.TRIFECTA)
