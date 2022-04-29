import pickle
from typing import List

import pandas as pd

from Betting.Bet import Bet
from Betting.TrifectaBettor import TrifectaBettor
from Betting.WinBettor import WinBettor
from DataCollection.RawRaceCardFactory import RawRaceCardFactory
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.NeuralNetworkRanker import NeuralNetworkRanker
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.SampleEncoder import SampleEncoder


class ProductionBettor:

    __ESTIMATOR_PATH = "data/estimator_v1-00.dat"
    __estimator: BoostedTreesRanker

    def __init__(self):
        self.__bettor = WinBettor()
        self.__encoder = SampleEncoder(FeatureManager(report_missing_features=True))

        with open(self.__ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

    def bet(self, race_id: str) -> dict:
        raw_race_card_factory = RawRaceCardFactory()
        raw_race_card = raw_race_card_factory.run(race_id)
        race_card = RaceCard(raw_race_card)

        raw_samples = self.__encoder.transform([race_card])

        samples = self.__estimator.transform(raw_samples)
        bet = self.__bettor.bet(samples)[0]
        predicted_winner_names = {(i+1): race_card.get_name_of_horse(bet.runner_ids[i]) for i in range(len(bet.runner_ids))}
        return predicted_winner_names


def main():
    production_bettor = ProductionBettor()
    predicted_winner_names = production_bettor.bet("4997909")
    print(f"Bet on runners: {predicted_winner_names}.")


if __name__ == '__main__':
    main()
