from typing import List

from Betting.Bets.Bet import Bet


class BettingSlip:

    def __init__(self):
        self.__bets: List[Bet] = []
        self.__win = 0

        self.conditional_ev = 0
        self.conditional_odds = 0

    def add_bet(self, bet: Bet):
        self.__bets.append(bet)
        self.conditional_ev += bet.success_probability * bet.odds - (1 + Bet.BET_TAX)
        self.conditional_odds += bet.odds - (1 + Bet.BET_TAX)

    def update_win(self, bet: Bet):
        self.__win += bet.potential_win

    @property
    def bets(self):
        return self.__bets

    @property
    def win(self) -> float:
        return self.__win

    @property
    def loss(self) -> float:
        return sum([bet.loss for bet in self.__bets])

    @property
    def payout(self) -> float:
        return self.__win - self.loss

