from typing import Dict, List

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Experiments.FundHistorySummary import FundHistorySummary
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, bettor: Bettor, bet_evaluator: BetEvaluator):
        self.estimator = estimator
        self.bettor = bettor
        self.bet_evaluator = bet_evaluator

    def fit_estimator(self, train_samples: DataFrame, validation_samples: DataFrame):
        self.estimator.fit(train_samples, validation_samples)

    def fund_history_summary(self, race_cards: Dict[str, RaceCard], samples: DataFrame, name: str) -> FundHistorySummary:
        estimated_samples = self.estimator.transform(samples)

        betting_slips = self.bettor.bet(race_cards, estimated_samples)
        betting_slips = self.bet_evaluator.update_wins(betting_slips)
        fund_history_summary = FundHistorySummary(name, betting_slips, start_wealth=200)

        return fund_history_summary

    def __str__(self) -> str:
        return f"{self.bettor.expected_value_additional_threshold}/{self.estimator.search_params}/{self.estimator.features}"

    @property
    def features(self) -> List[FeatureExtractor]:
        return self.estimator.features
