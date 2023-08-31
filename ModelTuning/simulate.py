import pickle

from tqdm import tqdm

from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.Ranking.BoostedTreesRanker import BoostedTreesRanker
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.simulate_conf import N_CONTAINER_MONTHS, N_MONTHS_TRAIN_SAMPLE, N_MONTHS_FORWARD_OFFSET, \
    NN_CLASSIFIER_PARAMS, __TEST_PAYOUTS_PATH, N_MONTHS_TEST_SAMPLE
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder


def optimize_model_configuration():
    feature_manager = FeatureManager()

    race_cards_loader = RaceCardsPersistence("race_cards")
    model_evaluator = ModelEvaluator()
    race_cards_array_factory = RaceCardsArrayFactory(feature_manager, model_evaluator)

    file_names = race_cards_loader.race_card_file_names

    container_race_card_file_names = file_names[N_MONTHS_FORWARD_OFFSET:N_MONTHS_FORWARD_OFFSET + N_CONTAINER_MONTHS]

    print(container_race_card_file_names)

    for race_card_file_name in tqdm(container_race_card_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
        race_cards_array_factory.race_cards_to_array(race_cards)

    # features not known from the container race card
    # TODO: this throws an indexerror when containers are none
    container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_race_card_file_names)
    container_race_cards = list(container_race_cards.values())
    columns = container_race_cards[0].attributes + feature_manager.feature_names
    train_sample_encoder = SampleEncoder(feature_manager.features, columns)

    first_month_train_sample = N_MONTHS_FORWARD_OFFSET + N_CONTAINER_MONTHS
    last_month_train_sample = first_month_train_sample + N_MONTHS_TRAIN_SAMPLE
    train_sample_file_names = file_names[first_month_train_sample:last_month_train_sample]

    for race_card_file_name in tqdm(train_sample_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

        for race_card in race_cards.values():
            race_card.horses = race_card.runners

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        train_sample_encoder.add_race_cards_arr(arr_of_race_cards)

    first_month_test_sample = last_month_train_sample
    last_month_test_sample = first_month_test_sample + N_MONTHS_TEST_SAMPLE
    test_sample_file_names = file_names[first_month_test_sample:last_month_test_sample]

    test_sample_encoder = SampleEncoder(feature_manager.features, columns)

    test_race_cards = {}

    for race_card_file_name in tqdm(test_sample_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        test_race_cards.update(race_cards)

    race_cards_sample = train_sample_encoder.get_race_cards_sample()
    race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

    # block_splitter = BlockSplitter(
    #     race_cards_sample,
    #     n_validation_rounds=5,
    #     n_test_races=N_TEST_RACES,
    # )

    # estimator = BoostedTreesRanker(feature_manager, model_evaluator, block_splitter)
    estimator = NNClassifier(feature_manager, model_evaluator, NN_CLASSIFIER_PARAMS)

    test_race_cards = {
        race_key: race_card for race_key, race_card in test_race_cards.items()
        if race_card.category in ["HCP", "LST"]
    }

    bets = model_evaluator.get_bets_of_model(estimator, train_sample_encoder, test_sample_encoder, test_race_cards)

    with open(__TEST_PAYOUTS_PATH, "wb") as f:
        pickle.dump(bets, f)

    # with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
    #     pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    optimize_model_configuration()
    print("finished")
