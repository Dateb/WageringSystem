from typing import List

from Betting.Bets.Bet import Bet


class BettingSlip:

    def __init__(self, race_id: str):
        self.race_id = race_id
        self.bets: List[Bet] = []
        self.win = 0
        self.loss = 0

        self.conditional_ev = 0
        self.conditional_odds = 0
        self.success_probability = 0

    def add_bet(self, bet: Bet):
        self.bets.append(bet)
        self.conditional_ev += bet.success_probability * bet.odds * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)
        self.conditional_odds += bet.odds - (1 + Bet.BET_TAX)

        self.loss += bet.loss
        self.success_probability += bet.success_probability

    def update_win(self, bet: Bet):
        bet.win = bet.potential_win
        self.win += bet.win

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
    def json(self) -> dict:
        betting_slip_json = {}

        return betting_slip_json

    @property
    def payout_percentage(self) -> float:
        return self.win - self.loss
