from copy import deepcopy
from datetime import timedelta
from typing import Dict, List

import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.Estimator import Estimator
from Model.Probabilizing.WinProbabilizer import WinProbabilizer
from ModelTuning.simulate_conf import MAX_HORSES_PER_RACE
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.SampleEncoder import SampleEncoder
from market_simulation.odds_history import create_bets, BetfairOfferContainer, WinOracle, create_race_key, Bet


class ModelEvaluator:

    def __init__(self):
        self.offer_container = BetfairOfferContainer()
        self.win_results = {}

    def add_results_from_race_cards(self, race_cards: Dict[str, RaceCard]):
        for race_card in race_cards.values():
            race_datetime = race_card.datetime - timedelta(hours=2)
            race_key = create_race_key(race_datetime, race_card.track_name)
            self.win_results[race_key] = {horse.name.replace("'", "").upper(): horse.has_won for horse in race_card.runners}

    def get_bets_of_model(self, estimator: Estimator, train_sample_encoder: SampleEncoder, test_sample_encoder: SampleEncoder) -> List[Bet]:
        train_sample = train_sample_encoder.get_race_cards_sample()
        test_sample = test_sample_encoder.get_race_cards_sample()

        train_sample.race_cards_dataframe = self.prune_sample(train_sample.race_cards_dataframe)
        test_sample.race_cards_dataframe = self.prune_sample(test_sample.race_cards_dataframe)

        scores = estimator.predict(train_sample, test_sample)
        estimation_result = WinProbabilizer().create_estimation_result(deepcopy(test_sample), scores)

        best_payout_sum = -np.inf
        best_bets = []

        bet_thresholds = [1.0 + (i / 10) for i in range(100)]
        win_oracle = WinOracle(self.win_results)
        for bet_threshold in bet_thresholds:
            bets = create_bets(estimation_result, self.offer_container, bet_threshold=bet_threshold)

            win_oracle.insert_payouts_into_bets(bets)

            payouts = [bet.payout for bet in bets]
            payout_sum = sum(payouts)

            if payout_sum > best_payout_sum:
                best_bets = bets
                best_payout_sum = payout_sum
                print(f"New best score: {best_payout_sum} at threshold: {bet_threshold}")

        return best_bets

    def prune_sample(self, race_cards_df):
        race_id_counts = race_cards_df[RaceCard.RACE_ID_KEY].value_counts()

        race_ids_to_keep = race_id_counts[race_id_counts <= MAX_HORSES_PER_RACE].index

        return race_cards_df[race_cards_df[RaceCard.RACE_ID_KEY].isin(race_ids_to_keep)]

