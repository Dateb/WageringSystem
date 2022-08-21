from typing import Dict

import pandas as pd

from Betting.BettingSlip import BetType, BettingSlip
from Betting.Bettor import Bettor
from DataAbstraction.Present.Horse import Horse


class FavoriteBettor(Bettor):

    def __init__(self, kelly_wealth: float):
        super().__init__(kelly_wealth)

    def _get_lowest_n_odds(self, samples: pd.DataFrame, n: int):
        race_groups = samples.groupby([Horse.RACE_ID_KEY]).apply(
            lambda x: x.sort_values([Horse.CURRENT_ODDS_KEY], ascending=True)
        ).reset_index(drop=True)

        return race_groups.groupby(Horse.RACE_ID_KEY).head(n)

    def bet(self, race_cards_sample: pd.DataFrame) -> Dict[str, BettingSlip]:
        bets_df = self._get_lowest_n_odds(race_cards_sample, 1)
        bets_df["stakes"] = self._kelly_wealth * 0.5

        print(bets_df)
        return self._dataframe_to_betting_slips(bets_df, bet_type=BetType.WIN)

