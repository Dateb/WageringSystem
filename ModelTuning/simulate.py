import pickle

import torch
from torch import nn
from tqdm import tqdm

from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.Ranking.BoostedTreesRanker import BoostedTreesRanker
from ModelTuning.ModelEvaluator import ModelEvaluator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.BlockSplitter import BlockSplitter

__FUND_HISTORY_SUMMARIES_PATH = "../data/fund_history_summaries.dat"
__BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

N_CONTAINER_MONTHS = 1
N_SAMPLE_MONTHS = 2
N_MONTHS_FORWARD_OFFSET = 111

N_TEST_RACES = 500

NN_CLASSIFIER_PARAMS = {
    "loss_function": nn.CrossEntropyLoss(),
    "base_lr": 1e-3,
    "decay_factor": 0.1,
    "patience": 5,
    "threshold": 1e-4,
    "eps": 1e-10,
    "lr_to_stop": 1e-6,
    "dropout_rate": 0.2
}


def optimize_model_configuration():
    feature_manager = FeatureManager()

    race_cards_loader = RaceCardsPersistence("race_cards")
    model_evaluator = ModelEvaluator()
    race_cards_array_factory = RaceCardsArrayFactory(race_cards_loader, feature_manager, model_evaluator)

    n_months = N_CONTAINER_MONTHS + N_SAMPLE_MONTHS
    container_race_card_file_names = race_cards_loader.race_card_file_names[N_MONTHS_FORWARD_OFFSET:N_MONTHS_FORWARD_OFFSET + N_CONTAINER_MONTHS]
    sample_race_card_file_names = race_cards_loader.race_card_file_names[N_MONTHS_FORWARD_OFFSET + N_CONTAINER_MONTHS:N_MONTHS_FORWARD_OFFSET + n_months]
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

    block_splitter = BlockSplitter(
        race_cards_sample,
        n_validation_rounds=5,
        n_test_races=N_TEST_RACES,
    )

    # estimator = BoostedTreesRanker(feature_manager, model_evaluator, block_splitter)
    estimator = NNClassifier(feature_manager, model_evaluator, block_splitter, NN_CLASSIFIER_PARAMS)

    fund_history_summary = model_evaluator.get_fund_history_summary_of_model(estimator, block_splitter)

    print(f"Final test set return: {fund_history_summary.score}")

    with open(__FUND_HISTORY_SUMMARIES_PATH, "wb") as f:
        pickle.dump(fund_history_summary, f)

    # for i in range(2):
    #     fund_history_summary = tuning_pipeline.get_test_fund_history_summary(bet_model_configuration)
    #     print(f"Result {i + 1}: {fund_history_summary.score}")
    #
    #
    # with open(__BET_MODEL_CONFIGURATION_PATH, "wb") as f:
    #     pickle.dump(bet_model_configuration, f)


if __name__ == '__main__':
    optimize_model_configuration()
    print("finished")
