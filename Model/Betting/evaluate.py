from abc import abstractmethod
from typing import List, Dict

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet
from ModelTuning import simulate_conf


class BetEvaluator:

    def __init__(self, win_results: Dict[str, RaceResult]):
        self.win_results = win_results

    def insert_payouts_into_bets(self, bets: List[Bet]) -> None:
        for bet in bets:
            race_key = str(bet.race_card.datetime)
            if race_key in self.win_results:
                horse_name = bet.bet_offer.horse_name.upper()
                if horse_name in self.win_results[race_key].horse_names:
                    bet.payout -= bet.stakes

                    if self.is_winning_bet(race_key, horse_name):
                        if simulate_conf.MARKET_TYPE == "WIN":
                            win_amount = bet.stakes * bet.bet_offer.odds * bet.bet_offer.adjustment_factor
                        else:
                            potential_winning = bet.stakes * (bet.bet_offer.odds - 1)
                            win_amount = potential_winning * bet.bet_offer.adjustment_factor + bet.stakes

                        bet.payout += win_amount * (1 - Bet.WIN_COMMISSION)

    @abstractmethod
    def is_winning_bet(self, race_key: str, horse_name: str) -> bool:
        pass


class WinBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str) -> bool:
        return self.win_results[race_key].get_place_of_horse_name(horse_name) == 1


class PlaceBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str) -> bool:
        win_result = self.win_results[race_key]
        return win_result.get_place_of_horse_name(horse_name) <= win_result.places_num
