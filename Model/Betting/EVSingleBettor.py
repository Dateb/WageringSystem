from typing import Dict, List

import numpy as np
from scipy.optimize import minimize

from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.WinBet import WinBet
from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Betting.kelly_optimizer import kelly_objective, kelly_jacobian
from Model.Betting.stakes_selection import get_multiple_win_stakes, get_highest_value_stakes, \
    get_most_probable_value_stakes
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
            win_probabilities = betting_slip.win_probabilities
            betting_odds = betting_slip.betting_odds

            # stakes = get_multiple_win_stakes(betting_slip.race_id, win_probabilities, betting_odds)
            # stakes = get_highest_value_stakes(self.ev_threshold, win_probabilities, betting_odds)
            stakes = get_most_probable_value_stakes(self.ev_threshold, win_probabilities, betting_odds)

            for i in range(len(stakes)):
                stakes_fraction = stakes[i]
                bet = WinBet(predicted_horse_results=[betting_slip.horse_results[i]], stakes_fraction=stakes_fraction)
                betting_slip.add_bet(bet)

        return betting_slips


