import os
import pickle
from copy import deepcopy
from typing import Dict, List

import numpy as np
from numpy import mean, std

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.bet import Bettor, Bet, BetfairOfferContainer
from Model.Betting.evaluate import WinBetEvaluator, PlaceBetEvaluator
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.Estimator import Estimator
from Model.Estimators.estimated_probabilities_creation import WinProbabilizer
from ModelTuning import simulate_conf
from ModelTuning.simulate_conf import MAX_HORSES_PER_RACE
from SampleExtraction.SampleEncoder import SampleEncoder


class ModelEvaluator:

    def __init__(self, race_results_container: RaceResultsContainer):
        self.race_results_container = race_results_container

    def get_bets_of_model(
            self,
            estimator: Estimator,
            train_sample_encoder: SampleEncoder,
            test_sample_encoder: SampleEncoder,
            test_race_cards: Dict[str, RaceCard]
    ) -> List[Bet]:
        train_sample = train_sample_encoder.get_race_cards_sample()
        test_sample = test_sample_encoder.get_race_cards_sample()

        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.sort_values(by="race_id")
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.sort_values(by="race_id")

        train_sample.race_cards_dataframe = self.prune_sample(train_sample.race_cards_dataframe)
        test_sample.race_cards_dataframe = self.prune_sample(test_sample.race_cards_dataframe)

        scores = estimator.predict(train_sample, test_sample)

        test_sample.race_cards_dataframe.to_csv("../data/test_races.csv")

        estimation_result = WinProbabilizer().create_estimation_result(deepcopy(test_sample), scores)

        best_payout_sum = -np.inf
        best_bets = []

        bet_thresholds = [1.0]

        if simulate_conf.MARKET_TYPE == "WIN":
            bet_evaluator = WinBetEvaluator(self.race_results_container.race_results)
        else:
            bet_evaluator = PlaceBetEvaluator(self.race_results_container.race_results)

        offer_container = self.get_bet_offer_container(test_race_cards)
        for bet_threshold in bet_thresholds:
            bets = Bettor(offer_container).bet(estimation_result, bet_threshold=bet_threshold)

            bet_evaluator.insert_payouts_into_bets(bets)

            payouts = [bet.payout for bet in bets if bet.bet_offer.odds < 20]
            payout_score = mean(payouts) / std(payouts)

            if payout_score > best_payout_sum:
                best_bets = bets
                best_payout_sum = payout_score
                print(f"New best score: {best_payout_sum} at threshold: {bet_threshold}")

        return best_bets

    def get_bet_offer_container(self, test_race_cards: Dict[str, RaceCard]) -> BetfairOfferContainer:
        if not os.path.isfile("../data/bet_offer_container.dat"):
            bet_offer_container = BetfairOfferContainer(test_race_cards)
            with open("../data/bet_offer_container.dat", "wb") as f:
                pickle.dump(bet_offer_container, f)
        else:
            with open("../data/bet_offer_container.dat", "rb") as f:
                bet_offer_container = pickle.load(f)

        return bet_offer_container

    def prune_sample(self, race_cards_df):
        race_id_counts = race_cards_df[RaceCard.RACE_ID_KEY].value_counts()

        race_ids_to_keep = race_id_counts[race_id_counts <= MAX_HORSES_PER_RACE].index

        return race_cards_df[race_cards_df[RaceCard.RACE_ID_KEY].isin(race_ids_to_keep)]

