from copy import deepcopy
from typing import Dict, List

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.BettingSlip import BettingSlip
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Experiments.FundHistorySummary import FundHistorySummary
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, bettor: Bettor):
        self.estimator = estimator
        self.bettor = bettor

    def fit_estimator(self, train_samples: DataFrame, num_boost_round: int):
        self.estimator.fit(train_samples, num_boost_round)

    def bet_on_race_cards_sample(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        estimated_race_cards_sample = self.estimator.transform(race_cards_sample)
        return self.bettor.bet(estimated_race_cards_sample)

    @property
    def features(self) -> List[FeatureExtractor]:
        return self.estimator.features
