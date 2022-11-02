from typing import Dict

from Betting.BetGenerators.PlaceBetGenerator import PlaceBetGenerator
from Betting.BetGenerators.WinBetGenerator import WinBetGenerator
from Betting.BettingSlip import BettingSlip
from Betting.Bettor import Bettor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class EVSingleBettor(Bettor):

    def __init__(
            self,
            additional_ev_threshold: float,
            lower_win_prob_threshold: float,
            upper_win_prob_threshold: float,
    ):
        bet_generators = [WinBetGenerator(additional_ev_threshold, lower_win_prob_threshold, upper_win_prob_threshold)]
        super().__init__(bet_generators)

    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        betting_slips = {}
        for i in range(len(race_cards_sample.race_keys)):
            betting_slips[race_cards_sample.race_keys[i]] = BettingSlip(race_cards_sample.race_ids[i])

        for bet_generator in self.bet_generators:
            bet_generator.add_multiple_bets(race_cards_sample, betting_slips)

        return betting_slips
