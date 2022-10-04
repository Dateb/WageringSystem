import pickle

from tqdm import tqdm

from Experiments.FundHistorySummary import FundHistorySummary
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

N_CONTAINER_MONTHS = 3
N_SAMPLE_MONTHS = 32

#Working Setup:
# 4 container, 21 sample, 2000 train, 3000 validation, 4 folds, 100 iter


class BetModelTuner:

    def __init__(self, feature_manager: FeatureManager, race_cards_sample: RaceCardsSample, model_evaluator: ModelEvaluator):
        self.feature_manager = feature_manager
        self.race_cards_sample = race_cards_sample
        self.sample_split_generator = SampleSplitGenerator(self.race_cards_sample, n_train_races=10000, n_races_per_fold=1650, n_folds=5)
        self.model_evaluator = model_evaluator

    def get_tuned_model_configuration(self) -> BetModelConfiguration:
        configuration_tuner = BetModelConfigurationTuner(
            race_cards_sample=self.race_cards_sample,
            feature_manager=self.feature_manager,
            sample_split_generator=self.sample_split_generator,
            model_evaluator=self.model_evaluator,
        )
        bet_model_configuration = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=20)

        return bet_model_configuration

    def get_test_fund_history_summary(self, bet_model_configuration: BetModelConfiguration) -> FundHistorySummary:
        bet_model = bet_model_configuration.create_bet_model()
        test_betting_slips = {}
        for i in range(self.sample_split_generator.n_folds):
            train_samples, test_samples = self.sample_split_generator.get_train_test_split(nth_test_fold=i)

            bet_model.fit_estimator(train_samples.race_cards_dataframe, None)

            fund_history_summary = self.model_evaluator.get_fund_history_summary_of_model(bet_model, test_samples)

            test_betting_slips = {**test_betting_slips, **fund_history_summary.betting_slips}

        return FundHistorySummary("Test run GBT", betting_slips=test_betting_slips)


def main():
    feature_manager = FeatureManager()

    race_cards_loader = RaceCardsPersistence("race_cards")
    container_race_card_file_names = race_cards_loader.race_card_file_names[:N_CONTAINER_MONTHS]
    container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_race_card_file_names)
    container_race_cards = list(container_race_cards.values())
    feature_manager.warmup_feature_sources(container_race_cards)

    if N_SAMPLE_MONTHS == -1:
        last_sample_container_idx = len(race_cards_loader.race_card_file_names)
    else:
        last_sample_container_idx = N_CONTAINER_MONTHS + N_SAMPLE_MONTHS
    sample_race_card_file_names = race_cards_loader.race_card_file_names[N_CONTAINER_MONTHS:last_sample_container_idx]

    model_evaluator = ModelEvaluator()
    race_cards_array_factory = RaceCardsArrayFactory(race_cards_loader, feature_manager, model_evaluator)

    # features not known from the container race card
    # TODO: this throws an indexerror when containers are none
    columns = container_race_cards[0].attributes + feature_manager.feature_names
    sample_encoder = SampleEncoder(feature_manager.features, columns)

    for race_card_file_name in tqdm(sample_race_card_file_names):
        arr_of_race_cards = race_cards_array_factory.generate_from_race_cards_file(race_card_file_name)
        sample_encoder.add_race_cards_arr(arr_of_race_cards)

    race_cards_sample = sample_encoder.get_race_cards_sample()

    race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

    tuning_pipeline = BetModelTuner(feature_manager, race_cards_sample, model_evaluator)
    bet_model_configuration = tuning_pipeline.get_tuned_model_configuration()
    fund_history_summary = tuning_pipeline.get_test_fund_history_summary(bet_model_configuration)

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summary, f)

    with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
        pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    main()
    print("finished")


    # race_arr_per_month = {}
    # while sample_race_card_file_names:
    #     next_file_names = sample_race_card_file_names[:4]
    #     sample_race_card_file_names = sample_race_card_file_names[4:]
    #
    #     extraction_threads = [
    #         SampleExtractionThread(race_cards_loader, feature_manager, race_cards_file_name, race_arr_per_month, model_evaluator)
    #         for race_cards_file_name in next_file_names
    #     ]
    #
    #     print(len(extraction_threads))
    #
    #     for extraction_thread in extraction_threads:
    #         extraction_thread.start()
    #
    #     for extraction_thread in extraction_threads:
    #         extraction_thread.join()
