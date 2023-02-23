from typing import Dict, List

from Model.Betting.BetGenerators.BetGenerator import BetGenerator
from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.PlaceBet import PlaceBet
from Model.Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.HorseResult import HorseResult


class PlaceBetGenerator(BetGenerator):

    def __init__(
            self,
            additional_ev_threshold: float,
            lower_win_prob_threshold: float,
            upper_win_prob_threshold: float,
    ):
        super().__init__(additional_ev_threshold, lower_win_prob_threshold, upper_win_prob_threshold)

    def add_bets(self, horse_results: List[HorseResult], betting_slips: Dict[str, BettingSlip]) -> None:
        for horse_result in horse_results:
            betting_slip = betting_slips[horse_result.race_date_time]

            expected_value = horse_result.expected_value

            if expected_value > (0.0 + self.additional_ev_threshold) and not betting_slip.bets:
                numerator = expected_value - self.additional_ev_threshold
                denominator = betting_slip.conditional_odds + horse_result.betting_odds - \
                              (1 + Bet.BET_TAX + self.additional_ev_threshold)
                stakes_fraction = numerator / denominator

                new_bet = PlaceBet([horse_result], stakes_fraction)

                betting_slip.add_bet(new_bet)
