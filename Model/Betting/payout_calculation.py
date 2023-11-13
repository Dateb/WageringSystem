from abc import ABC, abstractmethod
from typing import Dict, List

from DataAbstraction.Present.RaceResult import RaceResult
from Model.Betting.bet import Bet
from Model.Betting.evaluate import BetEvaluator
from ModelTuning import simulate_conf


class PayoutCalculator(ABC):

    def __init__(self, bet_evaluator: BetEvaluator):
        self.bet_evaluator = bet_evaluator

    @abstractmethod
    def insert_payouts_into_bets(self, bets: List[Bet], win_results: Dict[str, RaceResult]) -> None:
        pass


class BetfairPayoutCalculator(PayoutCalculator):

    WIN_COMMISSION = 0.025

    def insert_payouts_into_bets(self, bets: List[Bet], win_results: Dict[str, RaceResult]) -> None:
        for bet in bets:
            race_key = str(bet.bet_offer.race_card.datetime)
            if race_key in win_results:
                race_result = win_results[race_key]
                horse_name = bet.bet_offer.horse.name.upper()
                if horse_name in win_results[race_key].horse_names:
                    bet.loss = bet.stakes

                    if self.bet_evaluator.is_winning_bet(race_key, horse_name, race_result):
                        if simulate_conf.MARKET_TYPE == "WIN":
                            win_amount = bet.stakes * bet.bet_offer.odds * bet.bet_offer.adjustment_factor
                        else:
                            potential_winning = bet.stakes * (bet.bet_offer.odds - 1)
                            win_amount = potential_winning * bet.bet_offer.adjustment_factor + bet.stakes

                        bet.win = win_amount * (1 - self.WIN_COMMISSION)


class RacebetsPayoutCalculator(PayoutCalculator):

    TAX = 0.05

    def insert_payouts_into_bets(self, bets: List[Bet], win_results: Dict[str, RaceResult]) -> None:
        for bet in bets:
            race_key = str(bet.bet_offer.race_card.datetime)
            if race_key in win_results:
                race_result = win_results[race_key]
                horse_name = bet.bet_offer.horse.name.upper()
                if horse_name in win_results[race_key].horse_names:
                    bet.loss = bet.stakes * (1 + self.TAX)

                    if self.bet_evaluator.is_winning_bet(race_key, horse_name, race_result):
                        bet.win = bet.stakes * bet.bet_offer.odds
