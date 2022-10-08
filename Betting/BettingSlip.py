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

    def add_bet(self, bet: Bet):
        self.bets.append(bet)
        self.conditional_ev += bet.success_probability * bet.odds - (1 + Bet.BET_TAX)
        self.conditional_odds += bet.odds - (1 + Bet.BET_TAX)

        self.loss += bet.loss

    def update_win(self, bet: Bet):
        self.win += bet.potential_win

    @property
    def payout_percentage(self) -> float:
        return self.win - self.loss

