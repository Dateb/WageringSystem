from typing import List

from Betting.Bets.Bet import Bet
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceResult import RaceResult


class PlaceBet(Bet):

    def __init__(self, predicted_horse_results: List[HorseResult], stakes: float):
        super().__init__(predicted_horse_results, stakes)
        self.potential_win = predicted_horse_results[0].place_odds * stakes

    def is_won(self, race_result: RaceResult) -> bool:
        result_of_predicted_horse = race_result.get_result_of_horse_id(self.predicted_horse_results[0].horse_id)

        if result_of_predicted_horse is None:
            return False

        if result_of_predicted_horse.position in [1, 2]:
            return True

        return False