import pickle
from typing import Tuple

from Experiments.FundHistorySummary import FundHistorySummary
from Model.BetModel import BetModel
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSampleFactory import RaceCardsSampleFactory
from SampleExtraction.BlockSplitter import BlockSplitter

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"


class BetModelTuner:

    def __init__(self, n_warm_up_months: int = 1, n_sample_months: int = 1):
        self.feature_manager = FeatureManager()
        self.model_evaluator = ModelEvaluator()

        self.race_cards_sample_factory = RaceCardsSampleFactory(
            feature_manager=self.feature_manager,
            model_evaluator=self.model_evaluator,
            n_warm_up_months=n_warm_up_months,
            n_sample_months=n_sample_months,
        )
        self.race_cards_sample_factory.warm_up()
        self.race_cards_sample = self.race_cards_sample_factory.create_race_cards_sample()

        self.sample_splitter = BlockSplitter(
            self.race_cards_sample,
            n_validation_rounds=5,
            n_test_races=1,
        )

    def tune_model(self) -> Tuple[BetModel, FundHistorySummary]:
        achieved_positive_returns = True
        previous_p_diff = 0.82
        next_p_diff = previous_p_diff
        best_configuration = None
        configuration_tuner = None
        while achieved_positive_returns:
            previous_p_diff = next_p_diff
            next_p_diff = previous_p_diff - 0.02
            print(f"Finding model for p-diff: {next_p_diff}")
            configuration_tuner = BetModelConfigurationTuner(
                race_cards_sample=self.race_cards_sample,
                feature_manager=self.feature_manager,
                sample_splitter=self.sample_splitter,
                model_evaluator=self.model_evaluator,
                fractional_probability_distance=next_p_diff,
                max_tuning_rounds=5,
            )

            achieved_positive_returns = configuration_tuner.search_for_best_configuration()

            if achieved_positive_returns:
                best_configuration = configuration_tuner.best_configuration

        print(f"Lowest possible p-diff: {previous_p_diff}")

        train_sample, _ = self.sample_splitter.get_train_test_split()

        return best_configuration.create_bet_model(train_sample), configuration_tuner.get_test_fund_history_summary(best_configuration)


def main():
    tuning_pipeline = BetModelTuner(
        n_warm_up_months=1,
        n_sample_months=4,
    )
    bet_model, fund_history_summary = tuning_pipeline.tune_model()

    print(fund_history_summary.score)

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summary, f)


if __name__ == '__main__':
    main()
    print("finished")
