import pickle

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.DynamicKellyBettor import DynamicKellyBettor
from Betting.StaticKellyBettor import StaticKellyBettor
from DataAbstraction.RaceCard import RaceCard
from Experiments.FundHistorySummary import FundHistorySummary
from Experiments.SampleSet import SampleSet
from Persistence.RaceCardPersistence import RaceCardsPersistence
from Ranker.BoostedTreesRanker import BoostedTreesRanker
from Ranker.Ranker import Ranker
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

BEST_RANKER_PATH = "../data/best_ranker.dat"
FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"


class Validator:

    def __init__(self, bettor: Bettor, sample_set: SampleSet, bet_evaluator: BetEvaluator):
        self.__sample_set = sample_set
        self.bettor = bettor
        self.__bet_evaluator = bet_evaluator

    def fit_ranker(self, ranker: Ranker):
        ranker.fit(self.__sample_set.samples_train)

    def fund_history_summary(self, estimator: Ranker, name: str) -> FundHistorySummary:
        samples_test_estimated = estimator.transform(self.__sample_set.samples_test)

        betting_slips = self.bettor.bet(samples_test_estimated)
        betting_slips = self.__bet_evaluator.update_wins(betting_slips)
        fund_history_summary = FundHistorySummary(name, betting_slips)

        return fund_history_summary


def get_validator() -> Validator:
    raw_races = RaceCardsPersistence("train_race_cards").load_raw()
    race_cards = [RaceCard(race_id, raw_races[race_id], remove_non_starters=False) for race_id in raw_races]
    print(len(race_cards))

    sample_encoder = SampleEncoder(FeatureManager())
    samples = sample_encoder.transform(race_cards)
    sample_set = SampleSet(samples)
    bet_evaluator = BetEvaluator(raw_races)
    #bettor = DynamicKellyBettor(start_kelly_wealth=1000, kelly_fraction=0.33, bet_evaluator=bet_evaluator)
    bettor = StaticKellyBettor(start_kelly_wealth=1000)

    return Validator(bettor, sample_set, bet_evaluator)


def main():
    validator = get_validator()
    #with open(BEST_RANKER_PATH, "rb") as f:
    #    ranker = pickle.load(f)

    ranker = BoostedTreesRanker(["Current_Odds_Feature"], {})
    validator.fit_ranker(ranker)
    fund_history_summaries = [validator.fund_history_summary(ranker, name="Gradient Boosted Trees Ranker")]

    with open(FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)


if __name__ == '__main__':
    main()
    print("finished")
