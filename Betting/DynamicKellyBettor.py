from typing import Dict, List

import pandas as pd

from Betting.BetEvaluator import BetEvaluator
from Betting.BettingSlip import BettingSlip, BetType
from Betting.Bettor import Bettor


class DynamicKellyBettor(Bettor):

    def __init__(self, start_kelly_wealth: float, kelly_fraction: float, bet_evaluator: BetEvaluator):
        super().__init__(start_kelly_wealth)
        self.__kelly_fraction = kelly_fraction
        self.__bet_evaluator = bet_evaluator

    def bet(self, samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        bets_df = self._add_stakes_fraction(samples)

        if bets_df.empty:
            return {}

        bets_df["stakes"] = 0
        betting_slips = self._dataframe_to_betting_slips(bets_df, bet_type=BetType.WIN)

        return self.__bet_on_betting_slips_sequentially(betting_slips)

    def __bet_on_betting_slips_sequentially(self, betting_slips: Dict[str, BettingSlip]) -> Dict[str, BettingSlip]:
        kelly_wealth = self._start_kelly_wealth
        for betting_slip_key in betting_slips:
            betting_slip = betting_slips[betting_slip_key]
            for bet_key in betting_slip.bets:
                bet = betting_slip.bets[bet_key]
                stakes_fraction = bet.stakes_fraction
                stakes = kelly_wealth * self.__kelly_fraction * stakes_fraction
                betting_slip.set_stakes(bet, stakes)

            self.__bet_evaluator.update_wins({betting_slip.race_id: betting_slip})
            kelly_wealth += betting_slip.payout

        return betting_slips
