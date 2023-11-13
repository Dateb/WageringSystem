import os
import pickle
from copy import deepcopy
from typing import Dict, List

import numpy as np
from numpy import mean

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import Bettor, Bet
from Model.Betting.evaluate import WinBetEvaluator, PlaceBetEvaluator
from Model.Betting.offer_container import BetfairOfferContainer
from Model.Betting.payout_calculation import PayoutCalculator
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.Estimator import Estimator
from Model.Estimators.estimated_probabilities_creation import WinProbabilizer, PlaceProbabilizer
from ModelTuning import simulate_conf
from ModelTuning.simulate_conf import OFFER_CONTAINER
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder


class ModelEvaluator:

    def __init__(self, race_results_container: RaceResultsContainer):
        self.race_results_container = race_results_container

    def get_bets_of_model(
            self,
            estimator: Estimator,
            train_sample: RaceCardsSample,
            validation_sample: RaceCardsSample,
            test_sample: RaceCardsSample,
            test_race_cards: Dict[str, RaceCard]
    ) -> List[Bet]:
        scores = estimator.predict(train_sample, validation_sample, test_sample)

        test_sample.race_cards_dataframe.to_csv("../data/test_races.csv")

        estimation_result = simulate_conf.PROBABILIZER.create_estimation_result(deepcopy(test_sample), scores)

        best_payout_sum = -np.inf
        best_bets = []

        bet_thresholds = [0.5, 1.0, 1.5, 2.0]

        self.init_offer_container(test_race_cards)

        for bet_threshold in bet_thresholds:
            bettor = Bettor(bet_threshold=bet_threshold)
            bets = bettor.bet(OFFER_CONTAINER.race_offers, estimation_result)

            simulate_conf.PAYOUT_CALCULATOR.insert_payouts_into_bets(bets, self.race_results_container.race_results)

            payouts = [1 + bet.payout for bet in bets]
            payout_score = mean(payouts)

            print(f"Thresh/score: {bet_threshold}/{payout_score}")

            if payout_score > best_payout_sum:
                best_bets = bets
                best_payout_sum = payout_score
                print(f"New best score: {best_payout_sum} at threshold: {bet_threshold}")

            print(f"Offer acceptance rate: {bettor.offer_acceptance_rate}")

        return best_bets

    def init_offer_container(self, test_race_cards: Dict[str, RaceCard]):
        if not os.path.isfile(OFFER_CONTAINER.RACE_OFFERS_PATH):
            OFFER_CONTAINER.insert_race_cards(test_race_cards)
            OFFER_CONTAINER.save_race_offers()
        else:
            OFFER_CONTAINER.load_race_offers()

