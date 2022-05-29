import pickle

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.FavoriteBettor import FavoriteBettor
from Betting.FirstHorseBettor import FirstHorseBettor
from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.Ranker import Ranker
from Estimation.SampleSet import SampleSet
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder


class Validator:

    def __init__(self, bettor: Bettor, sample_set: SampleSet, raw_races: dict):
        self.__sample_set = sample_set
        self.bettor = bettor
        self.__bet_evaluator = BetEvaluator(raw_races)

    def fund_history_summary(self, estimator: Ranker, name: str) -> FundHistorySummary:
        estimator.fit(self.__sample_set.samples_train)
        samples_test_estimated = estimator.transform(self.__sample_set.samples_test)

        betting_slips = self.bettor.bet(samples_test_estimated)
        betting_slips = self.__bet_evaluator.update_wins(betting_slips)
        fund_history_summary = FundHistorySummary(name, betting_slips)

        return fund_history_summary


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

    fund_history_summaries = validator.train_validate_model(n_rounds=1, name="Gradient Boosted Trees Ranker")

    validator.bettor = FavoriteBettor(kelly_wealth=1000)
    fund_history_summaries += validator.train_validate_model(n_rounds=1, name="Favorite Bettor")

    validator.bettor = FirstHorseBettor(kelly_wealth=1000)
    fund_history_summaries += validator.train_validate_model(n_rounds=1, name="First Horse Bettor")

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__ESTIMATOR_PATH, "wb") as f:
        pickle.dump(validator.estimator, f)


if __name__ == '__main__':
    main()
