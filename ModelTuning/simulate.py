import pickle
from typing import List, Tuple

import numpy as np
from tqdm import tqdm

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.Ensemble.ensemble_average import EnsembleAverageEstimator
from Model.Estimators.Ranking.BoostedTreesRanker import BoostedTreesRanker
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from ModelTuning.simulate_conf import N_MONTHS_FORWARD_OFFSET, \
    NN_CLASSIFIER_PARAMS, TEST_PAYOUTS_PATH, N_MONTHS_TEST_SAMPLE, ESTIMATOR_PATH, \
    CONTAINER_UPPER_LIMIT_PERCENTAGE, TRAIN_UPPER_LIMIT_PERCENTAGE
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder


def split_race_card_files(file_names: List[str]) -> Tuple[List[str], List[str], List[str], List[str]]:
    non_test_sample_file_names = file_names[N_MONTHS_FORWARD_OFFSET:-N_MONTHS_TEST_SAMPLE]
    container_file_names, train_file_names, validation_file_names = np.split(
        non_test_sample_file_names,
        [
            int(len(non_test_sample_file_names) * CONTAINER_UPPER_LIMIT_PERCENTAGE),
            int(len(non_test_sample_file_names) * TRAIN_UPPER_LIMIT_PERCENTAGE)
         ]
    )
    test_file_names = file_names[-N_MONTHS_TEST_SAMPLE:]

    return container_file_names, train_file_names, validation_file_names, test_file_names


def optimize_model_configuration():
    feature_manager = FeatureManager()

    race_cards_loader = RaceCardsPersistence("race_cards")
    race_cards_array_factory = RaceCardsArrayFactory(feature_manager)

    file_names = race_cards_loader.race_card_file_names
    container_file_names, train_file_names, validation_file_names, test_file_names = split_race_card_files(file_names)

    print(len(container_file_names))
    print(len(train_file_names))
    print(len(validation_file_names))
    print(len(test_file_names))

    for race_card_file_name in tqdm(container_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

        race_cards_array_factory.race_cards_to_array(race_cards)

    # features not known from the container race card
    # TODO: this throws an indexerror when containers are none
    container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_file_names)
    container_race_cards = list(container_race_cards.values())
    columns = container_race_cards[0].attributes + feature_manager.feature_names
    train_sample_encoder = SampleEncoder(feature_manager.features, columns)

    for race_card_file_name in tqdm(train_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        train_sample_encoder.add_race_cards_arr(arr_of_race_cards)

    validation_sample_encoder = SampleEncoder(feature_manager.features, columns)

    for race_card_file_name in tqdm(validation_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        validation_sample_encoder.add_race_cards_arr(arr_of_race_cards)

    test_sample_encoder = SampleEncoder(feature_manager.features, columns)

    test_race_cards = {}

    race_results_container = RaceResultsContainer()
    for race_card_file_name in tqdm(test_file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
        race_results_container.add_results_from_race_cards(race_cards)
        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        test_race_cards.update(race_cards)

    race_cards_sample = train_sample_encoder.get_race_cards_sample()
    race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

    model_evaluator = ModelEvaluator(race_results_container)

    test_race_cards = {
        race_key: race_card for race_key, race_card in test_race_cards.items()
        if race_card.category in ["HCP"]
    }

    train_sample = train_sample_encoder.get_race_cards_sample()
    validation_sample = validation_sample_encoder.get_race_cards_sample()
    test_sample = test_sample_encoder.get_race_cards_sample()

    train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.sort_values(by="race_id")
    validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.sort_values(by="race_id")
    test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.sort_values(by="race_id")

    print("Testing TreeRanker:")

    gbt_estimator = BoostedTreesRanker(feature_manager)
    # bets = model_evaluator.get_bets_of_model(
    #     gbt_estimator,
    #     train_sample,
    #     validation_sample,
    #     test_sample,
    #     test_race_cards
    # )

    print("Testing NNClassifier:")

    nn_estimator = NNClassifier(feature_manager, NN_CLASSIFIER_PARAMS)
    # bets = model_evaluator.get_bets_of_model(
    #     nn_estimator,
    #     train_sample,
    #     validation_sample,
    #     test_sample,
    #     test_race_cards
    # )

    ensemble_estimator = EnsembleAverageEstimator(feature_manager, [gbt_estimator, nn_estimator])

    bets = model_evaluator.get_bets_of_model(
        nn_estimator,
        train_sample,
        validation_sample,
        test_sample,
        test_race_cards
    )

    with open(TEST_PAYOUTS_PATH, "wb") as f:
        pickle.dump(bets, f)

    with open(ESTIMATOR_PATH, "wb") as f:
        pickle.dump(nn_estimator, f)


if __name__ == '__main__':
    optimize_model_configuration()
    print("finished")
