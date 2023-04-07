from typing import List

from Model.Betting.Bets.Bet import Bet
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class PlaceBet(Bet):

    def __init__(self, predicted_horse_results: List[HorseResult], stakes_fraction: float):
        super().__init__(predicted_horse_results, stakes_fraction)
        self.success_probability = predicted_horse_results[0].place_probability
        self.place_num = self.predicted_horse_results[0].place_num
        self.winning_positions = [i + 1 for i in range(self.place_num)]
        self.potential_win = predicted_horse_results[0].place_odds * stakes_fraction * (1 - Bet.WIN_COMMISION)

    def is_won(self, race_result: RaceResult) -> bool:
        result_of_predicted_winner = race_result.get_result_of_horse_number(self.predicted_horse_results[0].number)
        if result_of_predicted_winner is None:
            return False

        if result_of_predicted_winner.position in self.winning_positions:
            return True

        return False

    def __str__(self) -> str:
        bet_str = "Place bet:\n"
        bet_str += "---------------------------------------\n"
        bet_str += f"Horse number: {self.predicted_horse_results[0].number}\n"
        bet_str += f"Odds of horse: {self.predicted_horse_results[0].place_odds}\n"
        bet_str += f"(Fractional) stakes: {self.stakes_fraction}\n"
        bet_str += f"Potential win: {self.potential_win}\n"
        bet_str += f"Estimated success probability: {self.predicted_horse_results[0].place_probability}\n"
        bet_str += "---------------------------------------\n"
        return bet_str