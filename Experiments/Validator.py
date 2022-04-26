import pickle

import pandas as pd
from tqdm import trange

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.ExactaBettor import ExactaBettor
from Betting.RandomBettor import RandomBettor
from Betting.TrifectaBettor import TrifectaBettor
from Betting.WinBettor import WinBettor
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.NeuralNetworkRanker import NeuralNetworkRanker
from Estimation.SampleSet import SampleSet
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.Paths import SAMPLES_PATH

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__ESTIMATOR_PATH = "../data/estimator.dat"


class Validator:

    def __init__(self, sample_set: SampleSet, bettor: Bettor):
        self.__sample_set = sample_set
        self.__bettor = bettor
        self.__random_state = 0

        self.__fund_history_summaries = []
        self.__best_win_percentage = 0
        self.__best_estimator = None

    def train_validate_model(self, n_rounds=2):
        for _ in trange(n_rounds):
            estimator = BoostedTreesRanker()
            fund_history_summary = self.__create_random_fund_history(estimator)
            if fund_history_summary.win_percentage > self.__best_win_percentage:
                print(f"Best win percentage thus far: {fund_history_summary.win_percentage * 100}%")
                self.__best_win_percentage = fund_history_summary.win_percentage
                self.__best_estimator = estimator
            self.__fund_history_summaries.append(fund_history_summary)

    def __create_random_fund_history(self, estimator) -> FundHistorySummary:
        samples_train, samples_test = self.__sample_set.create_split(random_state=self.__random_state)
        self.__random_state += 1

        estimator.fit(samples_train)
        samples_test_estimated = estimator.transform(samples_test)

        bets = self.__bettor.bet(samples_test_estimated)
        bet_results = BetEvaluator().evaluate(bets)
        fund_history_summary = FundHistorySummary("Default", bet_results)

        return fund_history_summary

    @property
    def fund_history_summaries(self):
        return self.__fund_history_summaries

    @property
    def best_estimator(self):
        return self.__best_estimator


def main():
    samples = pd.read_csv(SAMPLES_PATH)

    #most_often_track_id = samples.groupby(["track_id"]).size().sort_values(ascending=False).head(1).index.values[0]
    #samples = samples[samples["track_id"] == most_often_track_id]

    sample_set = SampleSet(samples)
    bettor = WinBettor()

    validator = Validator(sample_set, bettor)
    validator.train_validate_model(n_rounds=10)

    fund_history_summaries = validator.fund_history_summaries
    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__ESTIMATOR_PATH, "wb") as f:
        pickle.dump(validator.best_estimator, f)


if __name__ == '__main__':
    main()
