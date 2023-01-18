from typing import Dict

from Betting.BetGenerators.PlaceBetGenerator import PlaceBetGenerator
from Betting.BetGenerators.WinBetGenerator import WinBetGenerator
from Betting.BettingSlip import BettingSlip
from Betting.Bettor import Bettor
from Estimators.EstimationResult import EstimationResult


class EVSingleBettor(Bettor):

    def __init__(
            self,
            additional_ev_threshold: float,
            lower_win_prob_threshold: float,
            upper_win_prob_threshold: float,
    ):
        bet_generators = [PlaceBetGenerator(additional_ev_threshold, lower_win_prob_threshold, upper_win_prob_threshold)]
        super().__init__(additional_ev_threshold, bet_generators)

    def bet(self, estimation_result: EstimationResult) -> Dict[str, BettingSlip]:
        betting_slips = {}
        for i in range(len(estimation_result.race_keys)):
            betting_slips[estimation_result.race_keys[i]] = BettingSlip(estimation_result.race_ids[i])

        for bet_generator in self.bet_generators:
            bet_generator.add_bets(estimation_result.horse_results, betting_slips)

        return betting_slips
