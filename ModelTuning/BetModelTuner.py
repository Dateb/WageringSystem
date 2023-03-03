import pickle

from tqdm import tqdm

from Experiments.FundHistorySummary import FundHistorySummary
from Model.Probabilizing.PlaceProbabilizer import PlaceProbabilizer
from Model.Probabilizing.WinProbabilizer import WinProbabilizer
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

N_CONTAINER_MONTHS = 12
N_SAMPLE_MONTHS = 87

PROBABILIZER = WinProbabilizer()


class BetModelTuner:

    def __init__(self, feature_manager: FeatureManager, race_cards_sample: RaceCardsSample, model_evaluator: ModelEvaluator):
        self.feature_manager = feature_manager
        self.race_cards_sample = race_cards_sample
        self.sample_split_generator = SampleSplitGenerator(
            self.race_cards_sample,
            n_races_per_fold=2200,
            n_folds=5,
        )
        self.model_evaluator = model_evaluator

    def get_tuned_model_configuration(self) -> BetModelConfiguration:
        configuration_tuner = BetModelConfigurationTuner(
            race_cards_sample=self.race_cards_sample,
            feature_manager=self.feature_manager,
            sample_split_generator=self.sample_split_generator,
            model_evaluator=self.model_evaluator,
            probabilizer=PROBABILIZER,
        )
        bet_model_configuration = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=100)

        return bet_model_configuration

    def get_test_fund_history_summary(self, bet_model_configuration: BetModelConfiguration) -> FundHistorySummary:
        test_betting_slips = {}
        for i in range(self.sample_split_generator.n_folds):
            train_samples, test_samples = self.sample_split_generator.get_train_test_split(nth_test_fold=i)

            bet_model = bet_model_configuration.create_bet_model(train_samples)

            fund_history_summary = self.model_evaluator.get_fund_history_summary_of_model(bet_model, test_samples)

            test_betting_slips = {**test_betting_slips, **fund_history_summary.betting_slips}

        return FundHistorySummary("Test run GBT", betting_slips=test_betting_slips)


def optimize_model_configuration():
    feature_manager = FeatureManager()

    race_cards_loader = RaceCardsPersistence("race_cards")
    model_evaluator = ModelEvaluator()
    race_cards_array_factory = RaceCardsArrayFactory(race_cards_loader, feature_manager, model_evaluator)

    n_months = N_CONTAINER_MONTHS + N_SAMPLE_MONTHS
    container_race_card_file_names = race_cards_loader.race_card_file_names[:N_CONTAINER_MONTHS]
    sample_race_card_file_names = race_cards_loader.race_card_file_names[N_CONTAINER_MONTHS:n_months]
    print(container_race_card_file_names)
    print(sample_race_card_file_names)
    for race_card_file_name in tqdm(container_race_card_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
        race_cards_array_factory.race_cards_to_array(race_cards)

    # features not known from the container race card
    # TODO: this throws an indexerror when containers are none
    container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_race_card_file_names)
    container_race_cards = list(container_race_cards.values())
    columns = container_race_cards[0].attributes + feature_manager.feature_names
    sample_encoder = SampleEncoder(feature_manager.features, columns)

    for race_card_file_name in tqdm(sample_race_card_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        sample_encoder.add_race_cards_arr(arr_of_race_cards)

    race_cards_sample = sample_encoder.get_race_cards_sample()

    race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

    tuning_pipeline = BetModelTuner(feature_manager, race_cards_sample, model_evaluator)
    bet_model_configuration = tuning_pipeline.get_tuned_model_configuration()

    for i in range(2):
        fund_history_summary = tuning_pipeline.get_test_fund_history_summary(bet_model_configuration)
        print(f"Result {i + 1}: {fund_history_summary.validation_score}")

        with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
            pickle.dump(fund_history_summary, f)

    with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
        pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    optimize_model_configuration()
    print("finished")
