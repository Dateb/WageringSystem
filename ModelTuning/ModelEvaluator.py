import os
from typing import Dict, List

import numpy as np
from numpy import mean

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import Bet, BettorFactory
from Model.Betting.evaluate import WinBetEvaluator, PlaceBetEvaluator
from Model.Betting.offer_container import BetfairOfferContainer, RaceBetsOfferContainer
from Model.Betting.payout_calculation import RacebetsPayoutCalculator, BetfairPayoutCalculator
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.estimated_probabilities_creation import EstimationResult
from ModelTuning import simulate_conf


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


class ModelEvaluator:

    def __init__(self, race_results_container: RaceResultsContainer):
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

    def get_bets_of_model(
            self,
            estimation_result: EstimationResult,
            test_race_cards: Dict[str, RaceCard],
    ) -> List[Bet]:
        self.init_offer_container(test_race_cards)

        best_payout_score = -np.inf
        best_bets = []
        bet_thresholds = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]

        for bet_threshold in bet_thresholds:
            bettor = self.bettor_factory.create_bettor(bet_threshold)
            bets = bettor.bet(self.offer_container.race_offers, estimation_result)

            self.payout_calculator.insert_payouts_into_bets(bets, self.race_results_container.race_results)

            payouts = [bet.payout for bet in bets]
            payout_score = mean(payouts)

            print(f"Thresh/score: {bet_threshold}/{payout_score}")

            if payout_score > best_payout_score:
                best_bets = bets
                best_payout_score = payout_score
                print(f"New best score: {best_payout_score} at threshold: {bet_threshold}")

            print(f"Offer acceptance rate: {bettor.offer_acceptance_rate}")

        return best_bets

    def init_offer_container(self, test_race_cards: Dict[str, RaceCard]):
        if not os.path.isfile(self.offer_container.race_offers_path):
            self.offer_container.insert_race_cards(test_race_cards)
            self.offer_container.save_race_offers()
        else:
            self.offer_container.load_race_offers()

