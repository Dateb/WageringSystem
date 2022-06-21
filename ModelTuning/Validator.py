import pickle
from pathlib import Path

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.DynamicKellyBettor import DynamicKellyBettor
from Betting.StaticKellyBettor import StaticKellyBettor
from DataAbstraction.RaceCard import RaceCard
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.RaceCardPersistence import RaceCardsPersistence
from Ranker.BoostedTreesRanker import BoostedTreesRanker
from Ranker.Ranker import Ranker
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.Extractors.PastMaxSpeedSimilarDistanceExtractor import PastMaxSpeedSimilarDistanceExtractor
from SampleExtraction.Extractors.PreviousSpeedExtractor import PreviousSpeedExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

BEST_RANKER_PATH = "../data/best_ranker.dat"
FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"


class Validator:

    def __init__(self, bettor: Bettor, train_samples: DataFrame, test_samples: DataFrame, bet_evaluator: BetEvaluator):
        self.__train_samples = train_samples
        self.__test_samples = test_samples
        self.bettor = bettor
        self.__bet_evaluator = bet_evaluator

    def fit_ranker(self, ranker: Ranker):
        ranker.fit(self.__train_samples)

    def fund_history_summary(self, estimator: Ranker, name: str) -> FundHistorySummary:
        samples_test_estimated = estimator.transform(self.__test_samples)

        betting_slips = self.bettor.bet(samples_test_estimated)
        betting_slips = self.__bet_evaluator.update_wins(betting_slips)
        fund_history_summary = FundHistorySummary(name, betting_slips)

        return fund_history_summary


def get_validator() -> Validator:
    persistence = RaceCardsPersistence("train_race_cards")
    race_cards = persistence.load_every_month_non_writable()
    print(len(race_cards))

    sample_encoder = SampleEncoder(FeatureManager())
    train_samples, test_samples = sample_encoder.transform(race_cards)

    filepath = Path('data/out.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    test_samples.to_csv(filepath, index=False)

    bet_evaluator = BetEvaluator()
    #bettor = DynamicKellyBettor(start_kelly_wealth=1000, kelly_fraction=0.33, bet_evaluator=bet_evaluator)
    bettor = StaticKellyBettor(start_kelly_wealth=1000)

    return Validator(bettor, train_samples, test_samples, bet_evaluator)


def main():
    validator = get_validator()
    #with open(BEST_RANKER_PATH, "rb") as f:
    #    ranker = pickle.load(f)

    ranker_features = ["Current_Odds_Feature"]
    ranker = BoostedTreesRanker(ranker_features, {})
    validator.fit_ranker(ranker)

    fund_history_summaries = [validator.fund_history_summary(ranker, name="Gradient Boosted Trees Ranker - Current Odds")]

    ranker_features = FeatureManager.FEATURE_NAMES
    ranker = BoostedTreesRanker(ranker_features, {})
    validator.fit_ranker(ranker)

    fund_history_summaries += [validator.fund_history_summary(ranker, name="Gradient Boosted Trees Ranker - Current Odds + Speed features")]

    with open(FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(BEST_RANKER_PATH, "wb") as f:
        pickle.dump(ranker, f)


if __name__ == '__main__':
    main()
    print("finished")
