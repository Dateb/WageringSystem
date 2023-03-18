from typing import Dict, List

from DataAbstraction.Present.HorseResult import HorseResult
from Model.Betting.Bets.Bet import Bet
from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Estimation.RaceEventProbabilities import RaceEventProbabilities
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

    def bet(self, estimation_result: RaceEventProbabilities) -> Dict[str, BettingSlip]:
        betting_slips = {}
        for i in range(len(estimation_result.race_keys)):
            betting_slips[estimation_result.race_keys[i]] = BettingSlip(estimation_result.race_ids[i])

        self.add_bets_to_betting_slips(estimation_result.horse_results, betting_slips)

        return betting_slips

    def add_bets_to_betting_slips(self, horse_results: List[HorseResult], betting_slips: Dict[str, BettingSlip]) -> None:
        for horse_result in horse_results:
            betting_slip = betting_slips[horse_result.race_date_time]

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
