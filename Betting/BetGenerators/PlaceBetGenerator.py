from typing import Dict, List

from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.Bets.Bet import Bet
from Betting.Bets.PlaceBet import PlaceBet
from Betting.BettingSlip import BettingSlip
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

            single_ev = horse_result.place_odds * (1 - Bet.WIN_COMMISION) * horse_result.place_probability - (1 + Bet.BET_TAX)
            expected_value = betting_slip.conditional_ev + single_ev

            is_win_prob_in_between = self.lower_win_prob_threshold < horse_result.place_probability < self.upper_win_prob_threshold
            is_win_prob_on_lower_end = horse_result.place_probability < self.upper_win_prob_threshold < self.lower_win_prob_threshold
            is_win_prob_on_higher_end = self.upper_win_prob_threshold < self.lower_win_prob_threshold < horse_result.place_probability
            if is_win_prob_in_between or is_win_prob_on_lower_end or is_win_prob_on_higher_end:
                if expected_value > (0.0 + self.additional_ev_threshold):
                    # numerator = expected_value
                    # denominator = betting_slip.conditional_odds + horse_result.place_odds - (1 + Bet.BET_TAX)
                    # stakes_fraction = numerator / denominator
                    stakes_fraction = 0.06

                    new_bet = PlaceBet([horse_result], stakes_fraction)

                    betting_slip.add_bet(new_bet)
