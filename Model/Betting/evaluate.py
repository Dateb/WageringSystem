from abc import abstractmethod
from typing import List, Dict

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet, BetfairOddsVigAdjuster
from ModelTuning import simulate_conf


class BetEvaluator:

    @abstractmethod
    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult, bet: Bet) -> bool:
        pass


class WinBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult, bet: Bet) -> bool:
        return race_result.get_result_of_horse(horse_name).has_won


class PlaceBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult, bet: Bet) -> bool:
        horse = race_result.get_result_of_horse(horse_name)
        return horse.has_placed


def get_clv(offer_odds: float, starting_odds: float) -> float:
    offer_p = 1 / offer_odds
    starting_p = 1 / BetfairOddsVigAdjuster().get_adjusted_odds(starting_odds)
    return (starting_p - offer_p) / offer_p


def get_payout(offer_odds: float, has_won: bool) -> float:
    if has_won:
        return (offer_odds - 1) * 6 * (1 - 0.025)

    return -6
