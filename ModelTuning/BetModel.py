import pickle
from typing import Dict

from pandas import DataFrame

from Betting.BetEvaluator import BetEvaluator
from Betting.Bettor import Bettor
from DataAbstraction.Present.RaceCard import RaceCard
from Estimators.Ranker.BoostedTreesRanker import BoostedTreesRanker
from Experiments.FundHistorySummary import FundHistorySummary
from SampleExtraction.FeatureManager import FeatureManager

BEST_RANKER_PATH = "../data/best_ranker.dat"
FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"


class BetModel:

    def __init__(self, estimator: BoostedTreesRanker, bettor: Bettor, bet_evaluator: BetEvaluator):
        self.estimator = estimator
        self.bettor = bettor
        self.__bet_evaluator = bet_evaluator

    def fit_estimator(self, train_samples: DataFrame, validation_samples: DataFrame):
        self.estimator.fit(train_samples, validation_samples)

    def fund_history_summary(self, validation_race_cards: Dict[str, RaceCard], validation_samples: DataFrame, name: str) -> FundHistorySummary:
        samples_test_estimated = self.estimator.transform(validation_samples)

        betting_slips = self.bettor.bet(validation_race_cards, samples_test_estimated)
        betting_slips = self.__bet_evaluator.update_wins(betting_slips)
        fund_history_summary = FundHistorySummary(name, betting_slips)

        return fund_history_summary

    def __str__(self) -> str:
        return f"{self.bettor.expected_value_additional_threshold}/{self.estimator.search_params}/{self.estimator.feature_subset}"


def main():
    validator = get_bet_model()

    #ranker_features = ["Current_Odds_Feature"]
    ranker_features = FeatureManager.FEATURE_NAMES
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
