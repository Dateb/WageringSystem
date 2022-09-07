import pickle
from Experiments.FundHistorySummary import FundHistorySummary
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

N_CONTAINER_MONTHS = 2
N_SAMPLE_MONTHS = 3


class BetModelTuner:

    def __init__(self, feature_manager: FeatureManager, race_cards_sample: RaceCardsSample):
        self.feature_manager = feature_manager
        self.race_cards_sample = race_cards_sample
        self.sample_split_generator = SampleSplitGenerator(self.race_cards_sample)

    def get_tuned_model_configuration(self) -> BetModelConfiguration:
        configuration_tuner = BetModelConfigurationTuner(
            race_cards_sample=self.race_cards_sample,
            feature_manager=self.feature_manager,
            sample_split_generator=self.sample_split_generator,
        )
        bet_model_configuration = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=30)

        return bet_model_configuration

    def get_test_fund_history_summary(self, bet_model_configuration: BetModelConfiguration) -> FundHistorySummary:
        betting_slips = {}
        for i in range(self.sample_split_generator.test_width):
            bet_model = bet_model_configuration.create_bet_model()
            train_samples, test_samples = self.sample_split_generator.get_train_test_split(nth_test_fold=i)

            bet_model.fit_estimator(train_samples.race_cards_dataframe, None)

            estimated_samples = bet_model.estimator.transform(test_samples)

            new_betting_slips = bet_model.bettor.bet(estimated_samples)
            new_betting_slips = bet_model.bet_evaluator.update_wins(new_betting_slips)

            betting_slips = {**betting_slips, **new_betting_slips}

        return FundHistorySummary("GBT Test", betting_slips, start_wealth=200)


def main():
    feature_manager = FeatureManager()
    sample_encoder = SampleEncoder(feature_manager.features)

    race_cards_loader = RaceCardsPersistence("train_race_cards")
    container_race_card_file_names = race_cards_loader.race_card_file_names[:N_CONTAINER_MONTHS]
    container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_race_card_file_names)
    feature_manager.fit_enabled_container(list(container_race_cards.values()))

    if N_SAMPLE_MONTHS == -1:
        last_sample_container_idx = len(race_cards_loader.race_card_file_names)
    else:
        last_sample_container_idx = N_CONTAINER_MONTHS + N_SAMPLE_MONTHS
    sample_race_card_file_names = race_cards_loader.race_card_file_names[N_CONTAINER_MONTHS:last_sample_container_idx]

    for sample_race_card_file in sample_race_card_file_names:
        sample_race_cards = race_cards_loader.load_race_card_files_non_writable([sample_race_card_file])

        feature_manager.set_features(list(sample_race_cards.values()))
        sample_encoder.encode_race_cards(list(sample_race_cards.values()))

    race_cards_sample = sample_encoder.get_race_cards_sample()

    tuning_pipeline = BetModelTuner(feature_manager, race_cards_sample)
    bet_model_configuration = tuning_pipeline.get_tuned_model_configuration()
    fund_history_summaries = [tuning_pipeline.get_test_fund_history_summary(bet_model_configuration)]

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)

    with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
        pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    main()
    print("finished")
