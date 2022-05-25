import pickle
from typing import List

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

    def __init__(self, estimator: BoostedTreesRanker, bettor: Bettor, sample_set: SampleSet, raw_races: dict):
        self.__sample_set = sample_set
        self.__estimator = estimator
        self.__estimator.fit(self.__sample_set.samples_train)
        self.__random_state = 0

        self.__best_win_loss_ratio = 0
        self.__bettor = bettor
        self.__bet_evaluator = BetEvaluator(raw_races)

    def train_validate_model(self, n_rounds: int, name: str) -> List[FundHistorySummary]:
        fund_history_summaries = []
        for i in trange(n_rounds):
            fund_history_summary = self.create_random_fund_history(name, random_state=i+1)
            if fund_history_summary.win_loss_ratio > self.__best_win_loss_ratio:
                print(f"Best win/loss ratio thus far: {fund_history_summary.win_loss_ratio}")
                self.__best_win_loss_ratio = fund_history_summary.win_loss_ratio
            fund_history_summaries.append(fund_history_summary)

        return fund_history_summaries

    def create_random_fund_history(self, name: str, random_state: int) -> FundHistorySummary:
        samples_train, samples_test = self.__sample_set.create_split(random_state)
        samples_test_estimated = self.__estimator.transform(samples_test)

        bets = self.__bettor.bet(samples_test_estimated)
        bet_results = self.__bet_evaluator.evaluate(bets)
        fund_history_summary = FundHistorySummary(name, bet_results)

        return fund_history_summary

    @property
    def estimator(self):
        return self.__estimator


def main():
    raw_races = RaceCardsPersistence("train_race_cards").load_raw()
    race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]

    print(len(race_cards))
    sample_encoder = SampleEncoder(FeatureManager())
    samples = sample_encoder.transform(race_cards)
    sample_set = SampleSet(samples)
    bettor = WinBettor(kelly_wealth=1000)

    estimator = BoostedTreesRanker(feature_names=FeatureManager.FEATURE_NAMES, search_params={})
    validator = Validator(estimator, bettor, sample_set, raw_races)

    fund_history_summaries = validator.train_validate_model(n_rounds=2, name="Gradient Boosted Trees Ranker")

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__ESTIMATOR_PATH, "wb") as f:
        pickle.dump(validator.estimator, f)


if __name__ == '__main__':
    main()
