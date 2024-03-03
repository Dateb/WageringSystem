from abc import abstractmethod

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet, LiveResult


def get_payout(live_result: LiveResult, staking_size: float) -> float:
    if live_result.has_won:
        return (live_result.offer_odds - 1) * staking_size * (1 - 0.025)

    return -staking_size


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
