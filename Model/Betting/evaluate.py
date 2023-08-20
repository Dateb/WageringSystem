from typing import List

from Model.Betting.bet import Bet


class BetEvaluator:

    def __init__(self, win_results: dict):
        self.win_results = win_results

    def insert_payouts_into_bets(self, bets: List[Bet]) -> None:
        for bet in bets:
            race_key = str(bet.race_card.datetime)
            if race_key in self.win_results:
                horse_name = bet.bet_offer.horse_name.upper()
                if horse_name in self.win_results[race_key]:
                    bet.payout -= bet.stakes

                    if self.is_winning_bet(race_key, horse_name):
                        bet.payout += bet.stakes * bet.bet_offer.odds * (1 - Bet.WIN_COMMISSION)

    def is_winning_bet(self, race_key: str, horse_name: str) -> bool:
        return self.win_results[race_key][horse_name]
