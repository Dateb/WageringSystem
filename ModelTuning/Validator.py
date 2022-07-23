import pickle
from pathlib import Path

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from Betting.StaticKellyBettor import StaticKellyBettor
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Experiments.FundHistorySummary import FundHistorySummary
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

BEST_RANKER_PATH = "../data/best_ranker.dat"
FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"


class Validator:

    def __init__(self, bettor: Bettor, train_samples: DataFrame, test_samples: DataFrame, bet_evaluator: BetEvaluator):
        self.__train_samples = train_samples
        self.__validation_samples = test_samples
        self.bettor = bettor
        self.__bet_evaluator = bet_evaluator

    def fit_estimator(self, estimator):
        estimator.fit(self.__train_samples, self.__validation_samples)

    def fund_history_summary(self, estimator, name: str) -> FundHistorySummary:
        samples_test_estimated = estimator.transform(self.__validation_samples)

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
    train_samples.to_csv(filepath, index=False)

    bet_evaluator = BetEvaluator()
    bettor = StaticKellyBettor(sample_encoder.test_race_cards, start_kelly_wealth=1)

    return Validator(bettor, train_samples, test_samples, bet_evaluator)


def main():
    validator = get_validator()

    ranker_features = ["Current_Odds_Feature"]
    estimator = BoostedTreesRanker(ranker_features, {})
    validator.fit_estimator(estimator)

    fund_history_summaries = [validator.fund_history_summary(estimator, name="Gradient Boosted Trees Estimators - Current Odds + Speed features")]

    with open(FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(BEST_RANKER_PATH, "wb") as f:
         pickle.dump(estimator, f)


if __name__ == '__main__':
    main()
    print("finished")
