from typing import Dict

from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Betting.stakes_selection import get_stake_highest_market_deviation
from Model.Probabilizing.Probabilizer import Probabilizer


class EVSingleBettor(Bettor):

    def __init__(
            self,
            additional_ev_threshold: float,
            probabilizer: Probabilizer,
            stakes_fraction: float
    ):
        super().__init__(additional_ev_threshold, probabilizer)
        self.stakes_fraction = stakes_fraction

    def bet(self, betting_slips: Dict[str, BettingSlip]) -> Dict[str, BettingSlip]:
        for betting_slip in betting_slips.values():
            probabilities = self.probabilizer.get_probabilities(betting_slip)
            odds = self.probabilizer.get_odds(betting_slip)
            sp = self.probabilizer.get_sp(betting_slip)

            stakes = get_stake_highest_market_deviation(probabilities, odds, sp)

            for i in range(len(stakes)):
                stakes_fraction = stakes[i]
                bet = self.probabilizer.create_bet(
                    horse_result=betting_slip.horse_results[i],
                    stakes_fraction=stakes_fraction
                )
                betting_slip.add_bet(bet)

        return betting_slips


