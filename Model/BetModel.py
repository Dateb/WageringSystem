from copy import deepcopy
from typing import Dict, List

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.BettingSlip import BettingSlip
from Betting.Bettor import Bettor
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Experiments.FundHistorySummary import FundHistorySummary
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, bettor: Bettor):
        self.estimator = estimator
        self.bettor = bettor

    def fit_estimator(self, train_samples: DataFrame):
        self.estimator.fit(train_samples)

    @property
    def features(self) -> List[FeatureExtractor]:
        return self.estimator.features
