from typing import Dict, List

from pandas import DataFrame

from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Estimation.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Model.Probabilizing.Probabilizer import Probabilizer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, probabilizer: Probabilizer, bettor: Bettor):
        self.estimator = estimator
        self.probabilizer = probabilizer
        self.bettor = bettor

    def fit_estimator(self, train_samples: DataFrame, num_boost_round: int):
        self.estimator.fit(train_samples, num_boost_round)

    def bet_on_race_cards_sample(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        scores = self.estimator.score_races(race_cards_sample)
        race_event_probabilities = self.probabilizer.create_event_probabilities(race_cards_sample, scores)
        return self.bettor.bet(race_event_probabilities)

    @property
    def features(self) -> List[FeatureExtractor]:
        return self.estimator.features
