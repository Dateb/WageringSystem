import pickle
from time import sleep

from tqdm import tqdm

from Experiments.FundHistorySummary import FundHistorySummary
from Model.Probabilizing.PlaceProbabilizer import PlaceProbabilizer
from Model.Probabilizing.WinProbabilizer import WinProbabilizer
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSampleFactory import RaceCardsSampleFactory
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.BlockSplitter import BlockSplitter

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

N_CONTAINER_MONTHS = 1
N_SAMPLE_MONTHS = 1


class BetModelTuner:

    def __init__(self, feature_manager: FeatureManager, race_cards_sample: RaceCardsSample, model_evaluator: ModelEvaluator):
        self.feature_manager = feature_manager
        self.race_cards_sample = race_cards_sample
        self.block_splitter = BlockSplitter(
            self.race_cards_sample,
            n_validation_rounds=5,
            n_test_races=20,
        )
        self.model_evaluator = model_evaluator

    def get_tuned_model_configuration(self) -> BetModelConfiguration:
        achieved_positive_returns = True
        fractional_probability_distance = 0.8
        best_configuration = None
        while achieved_positive_returns:
            print(f"Finding model for p-diff: {fractional_probability_distance}")
            configuration_tuner = BetModelConfigurationTuner(
                race_cards_sample=self.race_cards_sample,
                feature_manager=self.feature_manager,
                sample_splitter=self.block_splitter,
                model_evaluator=self.model_evaluator,
                fractional_probability_distance=fractional_probability_distance,
                max_tuning_rounds=10,
            )

            achieved_positive_returns = configuration_tuner.search_for_best_configuration()

            if achieved_positive_returns:
                fractional_probability_distance -= 0.02
                best_configuration = configuration_tuner.best_configuration

        print(f"Lowest possible p-diff: {fractional_probability_distance + 0.02}")

        return best_configuration

    def get_test_fund_history_summary(self, bet_model_configuration: BetModelConfiguration) -> FundHistorySummary:
        train_sample, test_sample = self.block_splitter.get_train_test_split()

        bet_model = bet_model_configuration.create_bet_model(train_sample)
        return self.model_evaluator.get_fund_history_summary_of_model(bet_model, test_sample)


def optimize_model_configuration():
    feature_manager = FeatureManager()

    model_evaluator = ModelEvaluator()
    race_cards_sample_factory = RaceCardsSampleFactory(
        feature_manager=feature_manager,
        model_evaluator=model_evaluator,
        n_warm_up_months=1,
        n_sample_months=1,
    )

    race_cards_sample_factory.warm_up()
    race_cards_sample = race_cards_sample_factory.create_race_cards_sample()

    tuning_pipeline = BetModelTuner(feature_manager, race_cards_sample, model_evaluator)
    bet_model_configuration = tuning_pipeline.get_tuned_model_configuration()

    for i in range(2):
        fund_history_summary = tuning_pipeline.get_test_fund_history_summary(bet_model_configuration)
        print(f"Result {i + 1}: {fund_history_summary.score}")

        with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
            pickle.dump(fund_history_summary, f)

    with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
        pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    optimize_model_configuration()
    print("finished")
