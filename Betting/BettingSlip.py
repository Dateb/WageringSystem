from enum import Enum
from typing import Dict

from Betting.Bet import Bet


class BetType(Enum):

    WIN = 1
    EXACTA = 2
    TRIFECTA = 3


class BettingSlip:

    def __init__(self, bet_type: BetType):
        self.winner_id = "None"
        self.__bet_type = bet_type
        self.__bets: Dict[str, Bet] = {}
        self.__loss = 0
        self.__win = 0

    def add_bet(self, bet: Bet):
        self.__bets[bet.horse_id] = bet
        self.__loss += bet.loss

    def set_stakes(self, bet: Bet, stakes: float):
        if bet.horse_id in self.__bets:
            self.__loss -= bet.loss
        bet.set_stakes(stakes)
        self.add_bet(bet)

    def get_bet(self, horse_id: str) -> Bet:
        if horse_id in self.__bets:
            return self.__bets[horse_id]

    def update_won_bet(self, bet: Bet):
        self.__win = self.__bets[bet.horse_id].potential_win

    @property
    def bets(self):
        return self.__bets

    @property
    def win(self) -> float:
        return self.__win

    @property
    def loss(self) -> float:
        return self.__loss

    @property
    def payout(self) -> float:
        return self.__win - self.__loss

