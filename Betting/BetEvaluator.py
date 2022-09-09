from typing import Dict

from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.RaceResult import RaceResult


class BetEvaluator:

    def __init__(self, race_card_results: Dict[str, RaceResult]):
        self.race_card_results = race_card_results

    def add_wins_to_betting_slips(self, betting_slips: Dict[str, BettingSlip]) -> None:
        for date in betting_slips:
            betting_slip = betting_slips[date]
            race_result_of_betting_slip = self.race_card_results[date]
            for bet in betting_slip.bets:
                if bet.is_won(race_result_of_betting_slip):
                    betting_slip.update_win(bet)
