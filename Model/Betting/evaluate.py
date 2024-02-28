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
        return race_result.get_place_of_horse_name(horse_name) == 1


class PlaceBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult, bet: Bet) -> bool:
        n_horses = bet.bet_offer.n_horses
        places_num = 1
        if 5 <= n_horses <= 7:
            places_num = 2
        if 8 <= n_horses <= 15:
            places_num = 3
        if 16 <= n_horses:
            places_num = 4
        return 1 <= race_result.get_place_of_horse_name(horse_name) <= places_num


def get_clv(offer_odds: float, starting_odds: float) -> float:
    offer_p = 1 / offer_odds
    starting_p = 1 / BetfairOddsVigAdjuster().get_adjusted_odds(starting_odds)
    return (starting_p - offer_p) / offer_p
    # return offer_odds - starting_odds
    # if starting_odds > offer_odds:
    #     return -((starting_odds / offer_odds) - 1) - 0.025
    # else:
    #     return (offer_odds / starting_odds) - 1 - 0.025


def get_payout(offer_odds: float, has_won: bool) -> float:
    if has_won:
        return offer_odds * 6 * (1 - 0.025)

    return -6
