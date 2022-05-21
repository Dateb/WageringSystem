import pickle
from copy import copy
from tqdm import trange

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.FavoriteBettor import FavoriteBettor
from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.SampleSet import SampleSet
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__ESTIMATOR_PATH = "../data/estimator.dat"


class Validator:

    def __init__(self, sample_set: SampleSet, raw_races: dict):
        self.__sample_set = sample_set
        self.__random_state = 0

        self.__fund_history_summaries = []
        self.__best_win_loss_ratio = 0
        self.__estimator = BoostedTreesRanker()
        self.__best_estimator = None
        self.__bet_evaluator = BetEvaluator(raw_races)

    def train_validate_model(self, bettor: Bettor, n_rounds: int, name: str):
        for _ in trange(n_rounds):
            fund_history_summary = self.__create_random_fund_history(bettor, name)
            if fund_history_summary.win_loss_ratio > self.__best_win_loss_ratio:
                print(f"Best win/loss ratio thus far: {fund_history_summary.win_loss_ratio}")
                self.__best_win_loss_ratio = fund_history_summary.win_loss_ratio
                self.__best_estimator = copy(self.__estimator)
            self.__fund_history_summaries.append(fund_history_summary)

    def __create_random_fund_history(self, bettor: Bettor, name: str) -> FundHistorySummary:
        samples_train, samples_test = self.__sample_set.create_split(random_state=self.__random_state)
        self.__random_state += 1

        self.__estimator.fit(samples_train)
        samples_test_estimated = self.__estimator.transform(samples_test)

        bets = bettor.bet(samples_test_estimated)
        bet_results = self.__bet_evaluator.evaluate(bets)
        fund_history_summary = FundHistorySummary(name, bet_results)

        return fund_history_summary

    @property
    def fund_history_summaries(self):
        return self.__fund_history_summaries

    @property
    def best_estimator(self):
        return self.__best_estimator


def main():
    raw_races = RaceCardsPersistence("train_race_cards").load_raw()
    race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]

    print(len(race_cards))
    sample_encoder = SampleEncoder(FeatureManager())
    samples = sample_encoder.transform(race_cards)
    sample_set = SampleSet(samples)

    validator = Validator(sample_set, raw_races)
    #validator.train_validate_model(FavoriteBettor(), n_rounds=3, name="Favorite")
    validator.train_validate_model(WinBettor(kelly_wealth=10), n_rounds=3, name="Gradient Boosted Trees Ranker")

    fund_history_summaries = validator.fund_history_summaries
    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__ESTIMATOR_PATH, "wb") as f:
        pickle.dump(validator.best_estimator, f)


if __name__ == '__main__':
    main()
