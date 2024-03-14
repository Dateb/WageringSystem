import os
from typing import Dict, List

import numpy as np
from numpy import mean

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import Bet, BettorFactory, BetResult
from Model.Betting.evaluate import WinBetEvaluator, PlaceBetEvaluator
from Model.Betting.offer_container import BetfairOfferContainer, RaceBetsOfferContainer
from Model.Betting.payout_calculation import RacebetsPayoutCalculator, BetfairPayoutCalculator
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.estimated_probabilities_creation import EstimationResult
from ModelTuning import simulate_conf


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


class ModelEvaluator:

    def __init__(
            self,
            race_results_container: RaceResultsContainer,
            clv_tolerance: float = 0.025,
            drawdown_tolerance: float = 1000
    ):
        self.race_results_container = race_results_container
        self.bettor_factory = BettorFactory()

        if simulate_conf.MARKET_TYPE == "WIN":
            bet_evaluator = WinBetEvaluator()
        else:
            bet_evaluator = PlaceBetEvaluator()

        self.offer_container = BetfairOfferContainer()
        if simulate_conf.MARKET_SOURCE == "Racebets":
            self.payout_calculator = RacebetsPayoutCalculator(bet_evaluator)
        else:
            self.payout_calculator = BetfairPayoutCalculator(bet_evaluator)

        self.clv_tolerance = clv_tolerance
        self.drawdown_tolerance = drawdown_tolerance

    def get_bets_of_model(
            self,
            estimation_result: EstimationResult,
            test_race_cards: Dict[str, RaceCard],
    ) -> BetResult:
        self.init_offer_container(test_race_cards)

        best_bet_result = None
        bet_thresholds = [0.01]

        for bet_threshold in bet_thresholds:
            bettor = self.bettor_factory.create_bettor(bet_threshold)
            bet_result = bettor.bet(self.offer_container.race_offers, estimation_result)

            self.payout_calculator.insert_payouts_into_bets(bet_result.bets, self.race_results_container.race_results)

            clv = [bet.bet_offer.live_result.clv for bet in bet_result.bets]
            mean_clv = mean(clv)
            max_drawdown = bet_result.max_drawdown

            print(f"Thresh/Mean CLV/Max. Drawdown: {bet_threshold}/{mean_clv}/{max_drawdown}")

            if mean_clv > self.clv_tolerance and max_drawdown < self.drawdown_tolerance:
                best_bet_result = bet_result
                print(f"Picked new threshold: {bet_threshold}, according to selection criteria")

            print(f"Offer acceptance rate: {bettor.offer_acceptance_rate}")

        return best_bet_result

    def init_offer_container(self, test_race_cards: Dict[str, RaceCard]):
        if not os.path.isfile(self.offer_container.race_offers_path):
            self.offer_container.insert_race_cards(test_race_cards)
            self.offer_container.save_race_offers()
        else:
            self.offer_container.load_race_offers()

