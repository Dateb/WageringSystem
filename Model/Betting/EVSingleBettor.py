from typing import Dict, List

import numpy as np
from scipy.optimize import minimize

from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.WinBet import WinBet
from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Betting.kelly_optimizer import kelly_objective, kelly_jacobian
from Model.Probabilizing.Probabilizer import Probabilizer

previous_stakes: Dict[str, np.ndarray] = {}


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
        # self.add_bets_to_betting_slips(betting_slips)
        self.add_multiple_bets_to_betting_slips(betting_slips)

        return betting_slips

    def add_bets_to_betting_slips(self, betting_slips: Dict[str, BettingSlip]) -> None:
        for betting_slip in betting_slips.values():
            for horse_result in betting_slip.horse_results:
                expected_value = horse_result.expected_value

                if expected_value > (0.0 + self.additional_ev_threshold) and not betting_slip.bets:
                    numerator = expected_value - self.additional_ev_threshold
                    denominator = horse_result.betting_odds - \
                                  (1 + Bet.BET_TAX + self.additional_ev_threshold)
                    if denominator == 0:
                        print(horse_result.betting_odds)
                    stakes_fraction = (numerator / denominator) * self.stakes_fraction

                    new_bet = self.probabilizer.create_bet(horse_result, stakes_fraction)

                    betting_slip.add_bet(new_bet)

    def add_multiple_bets_to_betting_slips(self, betting_slips: Dict[str, BettingSlip]) -> None:
        for betting_slip in betting_slips.values():
            n_horses = len(betting_slip.horse_results)
            win_probabilities = betting_slip.win_probabilities
            betting_odds = betting_slip.betting_odds

            bounds = [(0, 1) for _ in range(len(win_probabilities))]
            if betting_slip.race_id in previous_stakes:
                init_stakes = previous_stakes[betting_slip.race_id]
            else:
                init_stakes = np.array([1 / n_horses for _ in range(n_horses)])

            result = minimize(
                fun=kelly_objective,
                jac=kelly_jacobian,
                x0=init_stakes,
                method="SLSQP",
                args=(win_probabilities, betting_odds),
                bounds=bounds,
                constraints=({'type': "ineq", "fun": lambda x: 1 - sum(x)})
            )

            previous_stakes[betting_slip.race_id] = result.x

            if -result.fun > self.additional_ev_threshold:
                for i in range(len(result.x)):
                    stakes_fraction = result.x[i]
                    bet = WinBet(predicted_horse_results=[betting_slip.horse_results[i]], stakes_fraction=stakes_fraction)
                    betting_slip.add_bet(bet)
