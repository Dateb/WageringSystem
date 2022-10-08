from typing import List

from Betting.Bets.Bet import Bet
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class ExactaBet(Bet):

    def __init__(self, predicted_horse_results: List[HorseResult], stakes_fraction: float):
        super().__init__(predicted_horse_results, stakes_fraction)
        self.stakes = stakes_fraction
        self.potential_win = 0

    def is_won(self, race_result: RaceResult) -> bool:
        if race_result.exacta_odds == 0:
            self.loss = 0
            return False

        place_1_predicted_horse = race_result.get_result_of_horse_id(self.predicted_horse_results[0].horse_id)
        place_2_predicted_horse = race_result.get_result_of_horse_id(self.predicted_horse_results[1].horse_id)

        if place_1_predicted_horse is None or place_2_predicted_horse is None:
            return False

        if place_1_predicted_horse.position == 1 and place_2_predicted_horse.position == 2:
            self.potential_win = self.stakes * race_result.exacta_odds
            return True

        return False