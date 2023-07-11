from copy import deepcopy
from datetime import timedelta
from typing import Dict

from Model.Betting.BetEvaluator import BetEvaluator
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.RaceResult import RaceResult
from Experiments.FundHistorySummary import FundHistorySummary
from Model.Betting.EVSingleBettor import EVSingleBettor
from Model.Estimators.Estimator import Estimator
from Model.Probabilizing.WinProbabilizer import WinProbabilizer
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.RaceCardsSample import RaceCardsSample
from market_simulation.odds_history import create_bets, BetfairOfferContainer, WinOracle, create_race_key


class ModelEvaluator:

    def __init__(self):
        self.offer_container = BetfairOfferContainer()
        self.win_results = {}

    def add_results_from_race_cards(self, race_cards: Dict[str, RaceCard]):
        for race_card in race_cards.values():
            race_datetime = race_card.datetime - timedelta(hours=2)
            race_key = create_race_key(race_datetime, race_card.track_name)
            self.win_results[race_key] = race_card.winner_name

    def get_fund_history_summary_of_model(self, estimator: Estimator, block_splitter: BlockSplitter) -> FundHistorySummary:
        train_sample, test_sample = block_splitter.get_train_test_split()

        train_sample.race_cards_dataframe = self.prune_sample(train_sample.race_cards_dataframe)
        test_sample.race_cards_dataframe = self.prune_sample(test_sample.race_cards_dataframe)

        scores = estimator.predict(train_sample, test_sample)
        estimation_result = WinProbabilizer().create_estimation_result(deepcopy(test_sample), scores)

        bets = create_bets(estimation_result, self.offer_container)

        print(bets)

        win_oracle = WinOracle(self.win_results)
        payout = win_oracle.get_payout(bets)

        #TODO: Why does the bettor need the probabilizer?
        bettor = EVSingleBettor(
            additional_ev_threshold=0.0,
            probabilizer=WinProbabilizer(),
        )

        # fund_history_summary = FundHistorySummary("Some Name", betting_slips)

        print(payout)

        return fund_history_summary

    def prune_sample(self, race_cards_df):
        race_id_counts = race_cards_df[RaceCard.RACE_ID_KEY].value_counts()

        race_ids_to_keep = race_id_counts[race_id_counts <= 20].index

        return race_cards_df[race_cards_df[RaceCard.RACE_ID_KEY].isin(race_ids_to_keep)]

