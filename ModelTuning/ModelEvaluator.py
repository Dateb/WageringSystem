from copy import deepcopy
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


class ModelEvaluator:

    def __init__(self):
        self.race_card_results: Dict[str, RaceResult] = {}

    def add_results_from_race_cards(self, race_cards: Dict[str, RaceCard]):
        for date in race_cards:
            self.race_card_results[date] = race_cards[date].race_result

    def get_fund_history_summary_of_model(self, estimator: Estimator, block_splitter: BlockSplitter) -> FundHistorySummary:
        bet_evaluator = BetEvaluator(self.race_card_results)

        train_sample, test_sample = block_splitter.get_train_test_split()

        train_sample.race_cards_dataframe = self.prune_sample(train_sample.race_cards_dataframe)
        test_sample.race_cards_dataframe = self.prune_sample(test_sample.race_cards_dataframe)

        scores = estimator.predict(train_sample, test_sample)
        betting_slips = WinProbabilizer().create_betting_slips(deepcopy(test_sample), scores)

        #TODO: Why does the bettor need the probabilizer?
        bettor = EVSingleBettor(
            additional_ev_threshold=0.0,
            probabilizer=WinProbabilizer(),
        )

        betting_slips = bettor.bet(betting_slips)

        bet_evaluator.add_wins_to_betting_slips(betting_slips)

        fund_history_summary = FundHistorySummary("Some Name", betting_slips)

        return fund_history_summary

    def prune_sample(self, race_cards_df):
        race_id_counts = race_cards_df[RaceCard.RACE_ID_KEY].value_counts()

        race_ids_to_keep = race_id_counts[race_id_counts <= 20].index

        return race_cards_df[race_cards_df[RaceCard.RACE_ID_KEY].isin(race_ids_to_keep)]

