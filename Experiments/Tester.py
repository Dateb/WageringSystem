import pickle
from datetime import date
from typing import List

import pandas as pd

from Betting.BetEvaluator import BetEvaluator
from Betting.WinBettor import WinBettor
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.PastRacesContainerPersistence import PastRacesContainerPersistence
from Persistence.RawRaceCardPersistence import RawRaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCard import RaceCard
from SampleExtraction.RaceCardsFilter import RaceCardsFilter
from SampleExtraction.SampleEncoder import SampleEncoder

TEST_RAW_RACE_CARDS_FILE_NAME: str = "test_raw_race_cards"
TEST_PAST_RACES_FILE_NAME: str = "test_past_races"

TEST_ESTIMATOR_PATH: str = "../data/estimator.dat"

TEST_FUND_HISTORY_SUMMARIES_PATH: str = "../data/fund_history_summaries.dat"


class Tester:

    def __init__(self, samples: pd.DataFrame, kelly_wealth: float = 20):
        self.__bettor = WinBettor(kelly_wealth)
        self.__samples = samples

        with open(TEST_ESTIMATOR_PATH, "rb") as f:
            self.__estimator = pickle.load(f)

    def run(self, name: str) -> List[FundHistorySummary]:
        samples_test_estimated = self.__estimator.transform(self.__samples)

        bets = self.__bettor.bet(samples_test_estimated)
        bet_results = BetEvaluator(TEST_RAW_RACE_CARDS_FILE_NAME).evaluate(bets)
        return [FundHistorySummary(name, bet_results)]


def main():
    raw_race_cards = RawRaceCardsPersistence(TEST_RAW_RACE_CARDS_FILE_NAME).load()
    race_cards = [RaceCard(raw_race_card) for raw_race_card in raw_race_cards]

    past_races_container = PastRacesContainerPersistence(TEST_PAST_RACES_FILE_NAME).load()

    race_cards = RaceCardsFilter(race_cards, past_races_container).get_race_cards_of_day(date(2022, 5, 3))

    sample_encoder = SampleEncoder(FeatureManager())
    test_samples = sample_encoder.transform(race_cards, past_races_container)

    tester = Tester(test_samples, kelly_wealth=10)
    fund_history_summaries = tester.run("Test run")

    with open(TEST_FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)


if __name__ == '__main__':
    main()
