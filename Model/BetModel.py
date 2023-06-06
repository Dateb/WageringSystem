from typing import Dict, List

from pandas import DataFrame

from Model.Betting.BettingSlip import BettingSlip
from Model.Betting.Bettor import Bettor
from Model.Estimators.BoostedTreesRanker import BoostedTreesRanker
from Model.Probabilizing.Probabilizer import Probabilizer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, probabilizer: Probabilizer, bettor: Bettor):
        self.estimator = estimator
        self.probabilizer = probabilizer
        self.bettor = bettor

    def fit_estimator(self, train_samples: DataFrame):
        self.estimator.fit(train_samples)

    def bet_on_race_cards_sample(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        scores = self.estimator.predict(race_cards_sample.race_cards_dataframe)
        betting_slips = self.probabilizer.create_betting_slips(race_cards_sample, scores)
        return self.bettor.bet(betting_slips)

    @property
    def features(self) -> List[FeatureExtractor]:
        return self.estimator.features
