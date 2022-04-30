import pickle
from typing import List, Tuple

import pandas as pd

from Betting.Bet import Bet
from Betting.TrifectaBettor import TrifectaBettor
from Betting.WinBettor import WinBettor
from DataCollection.PastRacesCollector import PastRacesCollector
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.NeuralNetworkRanker import NeuralNetworkRanker
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.PastRacesContainer import PastRacesContainer
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder


class ProductionBettor:

    __ESTIMATOR_PATH = "data/estimator_v1-01.dat"
    __estimator: BoostedTreesRanker

    def __init__(self, kelly_wealth: float = 100.0):
        self.__kelly_wealth = kelly_wealth
        self.__bettor = WinBettor()

        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

    def bet(self, race_id: str) -> Tuple[str, float]:
        raw_race_card_factory = RawRaceCardFactory()
        raw_race_card = raw_race_card_factory.run(race_id)
        race_card = RaceCard(raw_race_card)

        past_races_collector = PastRacesCollector([raw_race_card], initial_past_races={})
        past_races_collector.collect(n_past_races=200)

        raw_past_races = past_races_collector.past_races

        past_races_container = PastRacesContainer(raw_past_races)
        raw_samples = self.__encoder.transform([race_card], past_races_container)

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        name = race_card.get_name_of_horse(bet.runner_ids[0])
        stakes = bet.stakes * self.__kelly_wealth
        return name, stakes


def main():
    production_bettor = ProductionBettor()
    name, stakes = production_bettor.bet("5000653")
    print(f"Bet on horse: {name} this amount: {stakes}")


if __name__ == '__main__':
    main()
