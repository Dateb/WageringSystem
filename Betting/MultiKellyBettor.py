from typing import Dict

from Betting.BetGenerators.ExactaBetGenerator import ExactaBetGenerator
from Betting.BetGenerators.PlaceBetGenerator import PlaceBetGenerator
from Betting.BetGenerators.WinBetGenerator import WinBetGenerator
from Betting.BettingSlip import BettingSlip
from Betting.Bettor import Bettor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class MultiKellyBettor(Bettor):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        bet_generators = [WinBetGenerator(additional_ev_threshold, bet_limit)]
        super().__init__(bet_generators)

    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        betting_slips: Dict[str, BettingSlip] = {
            race_key: BettingSlip() for race_key in race_cards_sample.race_keys
        }

        for bet_generator in self.bet_generators:
            bet_generator.add_bets(race_cards_sample, betting_slips)

        return betting_slips
