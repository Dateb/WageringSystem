from abc import abstractmethod
from typing import List, Dict

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet
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
