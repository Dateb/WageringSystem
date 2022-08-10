from typing import Dict

import pandas as pd

from Betting.BettingSlip import BettingSlip, BetType
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard


class StaticKellyBettor(Bettor):

    def __init__(self, expected_value_additional_threshold: float, start_kelly_wealth: float):
        super().__init__(expected_value_additional_threshold, start_kelly_wealth)

    def bet(self, validation_race_cards: Dict[str, RaceCard], samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        if "stakes_fraction" not in samples.columns:
            samples = self._add_stakes_fraction(samples)
        samples["stakes"] = samples["stakes_fraction"] * self._start_kelly_wealth
        #bets_df.loc[bets_df["stakes"] < 0.5, "stakes"] = 0.0

        return self._dataframe_to_betting_slips(validation_race_cards, samples, bet_type=BetType.WIN)
