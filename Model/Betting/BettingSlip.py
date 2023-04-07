from typing import List

from DataAbstraction.Present.HorseResult import HorseResult
from Model.Betting.Bets.Bet import Bet


class BettingSlip:

    def __init__(self, race_id: str):
        self.race_id = race_id
        self.bets: List[Bet] = []
        self.win = 0
        self.loss = 0

        self.conditional_ev = 0
        self.conditional_odds = 0
        self.success_probability = 0
        self.horse_results: List[HorseResult] = []

    def add_horse_result(self, horse_result: HorseResult) -> None:
        self.horse_results.append(horse_result)

    def add_bet(self, bet: Bet):
        self.bets.append(bet)

        self.loss += bet.loss
        self.success_probability += bet.success_probability

    def update_win(self, bet: Bet):
        bet.win = bet.potential_win
        self.win += bet.win

    def __str__(self) -> str:
        betting_slip_str = f"Race ID: {self.race_id}"
        betting_slip_str += "Betting slip:\n"
        betting_slip_str += f"(Fractional) total loss: {self.loss}\n"
        betting_slip_str += "Bets:\n"
        betting_slip_str += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        for bet in self.bets:
            betting_slip_str += str(bet)
        betting_slip_str += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        return betting_slip_str

    @property
    def json(self) -> dict:
        betting_slip_json = {
            "race_id": self.race_id,
            "bets": [bet.json for bet in self.bets],
            "loss": self.loss
        }

        return betting_slip_json

    @property
    def payout_percentage(self) -> float:
        return self.win - self.loss
