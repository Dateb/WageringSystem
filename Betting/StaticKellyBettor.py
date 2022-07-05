from typing import Dict, List

import pandas as pd

from Betting.BettingSlip import BettingSlip, BetType
from Betting.Bettor import Bettor
from DataAbstraction.RaceCard import RaceCard


class StaticKellyBettor(Bettor):

    def __init__(self, race_cards: List[RaceCard], start_kelly_wealth: float):
        super().__init__(race_cards, start_kelly_wealth)

    def bet(self, samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        samples["stakes"] = samples["stakes_fraction"] * self._start_kelly_wealth
        #bets_df.loc[bets_df["stakes"] < 0.5, "stakes"] = 0.0

        return self._dataframe_to_betting_slips(samples, bet_type=BetType.WIN)
