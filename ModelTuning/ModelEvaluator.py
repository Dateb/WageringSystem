import os
from typing import Dict

import numpy as np
from numpy import mean

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import Bet, BettorFactory, BetResult
from Model.Betting.offer_container import BetfairOfferContainer
from Model.Betting.staking import FixedStakesCalculator
from Model.Estimation.estimated_probabilities_creation import EstimationResult
from ModelTuning import simulate_conf


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


class ModelEvaluator:

    def __init__(
            self,
            clv_tolerance: float = -np.inf,
            drawdown_tolerance: float = np.inf
    ):
        self.bettor_factory = BettorFactory()

        self.offer_container = BetfairOfferContainer()
        self.stakes_calculator = FixedStakesCalculator(fixed_stakes=6.0)

        self.clv_tolerance = clv_tolerance
        self.drawdown_tolerance = drawdown_tolerance

    def get_bets_of_model(
            self,
            estimation_result: EstimationResult,
            test_race_cards: Dict[str, RaceCard],
    ) -> BetResult:
        self.init_offer_container(test_race_cards)

        best_bet_result = None
        min_ev_values = [1.0]

        for min_ev_value in min_ev_values:
            bettor = self.bettor_factory.create_bettor(min_ev_value)
            bets = bettor.bet(self.offer_container.race_offers, estimation_result)
            bet_result = BetResult(bets)

            for bet in bets:
                self.stakes_calculator.set_stakes(bet)

            clv = [bet.bet_offer.live_result.clv for bet in bets]
            mean_clv = mean(clv)
            max_drawdown = bet_result.max_drawdown

            print(f"Thresh/Mean CLV/Max. Drawdown: {min_ev_value}/{mean_clv}/{max_drawdown}")

            if mean_clv > self.clv_tolerance and max_drawdown < self.drawdown_tolerance:
                best_bet_result = bet_result
                print(f"Picked new threshold: {min_ev_value}, according to selection criteria")

            print(f"Offer acceptance rate: {bettor.offer_acceptance_rate}")

        return best_bet_result

    def init_offer_container(self, test_race_cards: Dict[str, RaceCard]):
        if not os.path.isfile(self.offer_container.race_offers_path):
            self.offer_container.insert_race_cards(test_race_cards)
            self.offer_container.save_race_offers()
        else:
            self.offer_container.load_race_offers()

