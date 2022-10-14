from typing import List

from Betting.Bets.Bet import Bet


class BettingSlip:

    def __init__(self, race_id: str):
        self.race_id = race_id
        self.bets: List[Bet] = []
        self.success_probability = 0
        self.total_odds = 0
        self.win = 0
        self.loss = 0

        self.reserve_rate = 1

    def add_bet(self, bet: Bet):
        self.bets.append(bet)
        self.success_probability += bet.success_probability
        self.total_odds += bet.odds
        self.reserve_rate += (1 - self.success_probability) / (1 - (1 / self.total_odds))

        self.loss += bet.loss

    def update_win(self, bet: Bet):
        self.win += bet.potential_win

    def __str__(self) -> str:
        betting_slip_str = ""
        betting_slip_str += "Betting slip:\n"
        betting_slip_str += f"(Fractional) total loss: {self.loss}\n"
        betting_slip_str += "Bets:\n"
        betting_slip_str += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        for bet in self.bets:
            betting_slip_str += str(bet)
        betting_slip_str += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        return betting_slip_str

    @property
    def payout_percentage(self) -> float:
        return self.win - self.loss

