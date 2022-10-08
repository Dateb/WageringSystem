from typing import List

from Betting.Bets.Bet import Bet
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class WinBet(Bet):

    def __init__(self, predicted_horse_results: List[HorseResult], stakes_fraction: float, success_probability: float):
        super().__init__(predicted_horse_results, stakes_fraction, success_probability)
        self.potential_win = predicted_horse_results[0].win_odds * stakes_fraction
        self.odds = predicted_horse_results[0].win_odds

    def is_won(self, race_result: RaceResult) -> bool:
        result_of_predicted_winner = race_result.get_result_of_horse_id(self.predicted_horse_results[0].number)
        if result_of_predicted_winner is None:
            return False

        if result_of_predicted_winner.position == 1:
            return True

        return False
