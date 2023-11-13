from abc import abstractmethod
from typing import List, Dict

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet
from ModelTuning import simulate_conf


class BetEvaluator:

    @abstractmethod
    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult) -> bool:
        pass


class WinBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult) -> bool:
        return race_result.get_place_of_horse_name(horse_name) == 1


class PlaceBetEvaluator(BetEvaluator):

    def is_winning_bet(self, race_key: str, horse_name: str, race_result: RaceResult) -> bool:
        return 1 <= race_result.get_place_of_horse_name(horse_name) <= race_result.places_num
