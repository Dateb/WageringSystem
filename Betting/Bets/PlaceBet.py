from typing import List

from Betting.Bets.Bet import Bet
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class PlaceBet(Bet):

    def __init__(self, place_num: int, predicted_horse_results: List[HorseResult], stakes_fraction: float, success_probability: float):
        super().__init__(predicted_horse_results, stakes_fraction, success_probability)
        self.predicted_horse_result = predicted_horse_results[0]
        self.winning_positions = [i + 1 for i in range(place_num)]
        self.stakes_fraction = stakes_fraction
        self.loss = (stakes_fraction + Bet.BET_TAX) * 2
        self.potential_win = 0

    def is_won(self, race_result: RaceResult) -> bool:
        result_of_predicted_horse = race_result.get_result_of_horse_number(self.predicted_horse_result.number)

        if result_of_predicted_horse is None:
            return False

        if result_of_predicted_horse.position == 1:
            self.potential_win = self.predicted_horse_result.win_odds * self.stakes_fraction\
                                 + self.predicted_horse_result.place_odds * self.stakes_fraction
            return True

        if result_of_predicted_horse.position in self.winning_positions:
            self.potential_win = self.predicted_horse_result.place_odds * self.stakes_fraction
            return True

        return False