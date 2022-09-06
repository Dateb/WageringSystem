import pickle
from typing import List

from Model.BetModel import BetModel
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder

BET_MODEL_CONFIGURATION_PATH: str = "../data/bet_model_configuration.dat"
TEST_FUND_HISTORY_SUMMARIES_PATH: str = "../data/fund_history_summaries.dat"


def encode_from_files(bet_model: BetModel, race_cards_loader: RaceCardsPersistence, race_card_files: List[str]) -> RaceCardsSample:
    feature_manager = FeatureManager(features=bet_model.features)
    sample_encoder = SampleEncoder(features=bet_model.features)

    race_cards = race_cards_loader.load_race_card_files_non_writable(race_card_files)

    feature_manager.set_features(list(race_cards.values()))
    sample_encoder.encode_race_cards(list(race_cards.values()))

    return sample_encoder.get_race_cards_sample()


def main():
    with open(BET_MODEL_CONFIGURATION_PATH, "rb") as f:
        bet_model_configuration: BetModelConfiguration = pickle.load(f)

    bet_model = bet_model_configuration.create_bet_model()

    race_cards_loader = RaceCardsPersistence("train_race_cards")
    test_width = 4
    train_width = 15
    n_files = len(race_cards_loader.race_card_file_names)
    train_test_file_names = race_cards_loader.race_card_file_names[n_files - 1 - test_width - train_width:]

    train_race_card_files = train_test_file_names[:train_width]
    test_race_card_files = train_test_file_names[train_width:]

    train_race_cards_sample = encode_from_files(bet_model, race_cards_loader, train_race_card_files)
    test_race_cards_sample = encode_from_files(bet_model, race_cards_loader, test_race_card_files)

    bet_model.fit_estimator(train_samples=train_race_cards_sample.race_cards_dataframe, validation_samples=None)
    fund_history_summaries = [bet_model.get_fund_history_summary(race_cards_sample=test_race_cards_sample, name="Model loading run")]

    with open(TEST_FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summaries, f)


if __name__ == '__main__':
    main()
    print("finished")
