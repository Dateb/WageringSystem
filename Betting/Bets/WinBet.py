from Betting.Bets.Bet import Bet
from DataAbstraction.Present.RaceResult import RaceResult


class WinBet(Bet):

    TAX: float = 0.05

    def __init__(self, horse_id: str, odds: float, stakes: float, stakes_fraction: float):
        super().__init__(horse_id, odds, stakes, stakes_fraction)

    def is_won(self, race_result: RaceResult) -> bool:
        predicted_winner_result = race_result.get_result_of_horse_id(self.horse_id)
        if predicted_winner_result is None:
            return False

        if predicted_winner_result.position == 1:
            return True

        return False
