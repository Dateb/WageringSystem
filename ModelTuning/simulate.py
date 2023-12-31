import pickle
from copy import deepcopy

from tqdm import tqdm

from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimators.Classification.NNClassifier import NNClassifier
from Model.Estimators.Ensemble.ensemble_average import EnsembleAverageEstimator
from Model.Estimators.Ranking.BoostedTreesRanker import BoostedTreesRanker
from Model.Estimators.estimated_probabilities_creation import WinProbabilizer, PlaceProbabilizer
from ModelTuning import simulate_conf
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.simulate_conf import NN_CLASSIFIER_PARAMS, TEST_PAYOUTS_PATH, ESTIMATOR_PATH
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.data_splitting import MonthDataSplitter


class ModelSimulator:

    def __init__(self, month_data_splitter: MonthDataSplitter):
        self.month_data_splitter = month_data_splitter

        self.model_evaluator = None
        self.estimation_result = None
        self.test_race_cards = None

    def simulate_prediction(self) -> float:
        feature_manager = FeatureManager()

        race_cards_array_factory = RaceCardsArrayFactory(feature_manager)

        print(f"#container months: {len(self.month_data_splitter.container_file_names)}")
        print(f"#train months: {len(self.month_data_splitter.train_file_names)}")
        print(f"#validation months: {len(self.month_data_splitter.validation_file_names)}")
        print(f"#test months: {len(self.month_data_splitter.test_file_names)}")

        for race_card_file_name in tqdm(self.month_data_splitter.container_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            race_cards_array_factory.race_cards_to_array(race_cards)

        # features not known from the container race card
        # TODO: this throws an indexerror when containers are none
        container_race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable(self.month_data_splitter.container_file_names)
        container_race_cards = list(container_race_cards.values())
        columns = container_race_cards[0].attributes + feature_manager.feature_names
        train_sample_encoder = SampleEncoder(feature_manager.features, columns)

        for race_card_file_name in tqdm(self.month_data_splitter.train_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
            train_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        validation_sample_encoder = SampleEncoder(feature_manager.features, columns)

        for race_card_file_name in tqdm(self.month_data_splitter.validation_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
            validation_sample_encoder.add_race_cards_arr(arr_of_race_cards)

        test_sample_encoder = SampleEncoder(feature_manager.features, columns)

        test_race_cards = {}

        race_results_container = RaceResultsContainer()
        for race_card_file_name in tqdm(self.month_data_splitter.test_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            race_results_container.add_results_from_race_cards(race_cards)
            arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
            test_sample_encoder.add_race_cards_arr(arr_of_race_cards)

            test_race_cards.update(race_cards)

        race_cards_sample = train_sample_encoder.get_race_cards_sample()
        race_cards_sample.race_cards_dataframe.to_csv("../data/races.csv")

        self.model_evaluator = ModelEvaluator(race_results_container)

        self.test_race_cards = {
            race_key: race_card for race_key, race_card in test_race_cards.items()
            if race_card.category in ["HCP"]
        }

        train_sample = train_sample_encoder.get_race_cards_sample()
        validation_sample = validation_sample_encoder.get_race_cards_sample()
        test_sample = test_sample_encoder.get_race_cards_sample()

        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.sort_values(by="race_id")
        validation_sample.race_cards_dataframe = validation_sample.race_cards_dataframe.sort_values(by="race_id")
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.sort_values(by="race_id")

        # TODO: remove saving from function
        # test_sample.race_cards_dataframe.to_csv("../data/test_races.csv")

        nn_estimator = NNClassifier(feature_manager, NN_CLASSIFIER_PARAMS)
        gbt_estimator = BoostedTreesRanker(feature_manager)

        estimator = gbt_estimator

        ensemble_estimator = EnsembleAverageEstimator(feature_manager, [gbt_estimator, nn_estimator])

        scores, test_loss = estimator.predict(train_sample, validation_sample, test_sample)

        if simulate_conf.MARKET_TYPE == "WIN":
            probabilizer = WinProbabilizer()
        else:
            probabilizer = PlaceProbabilizer()

        self.estimation_result = probabilizer.create_estimation_result(deepcopy(test_sample), scores)

        # TODO: remove saving from function
        with open(ESTIMATOR_PATH, "wb") as f:
            pickle.dump(estimator, f)

        return test_loss

    def simulate_betting(self) -> None:
        bets = self.model_evaluator.get_bets_of_model(self.estimation_result, self.test_race_cards)

        with open(TEST_PAYOUTS_PATH, "wb") as f:
            pickle.dump(bets, f)


if __name__ == '__main__':
    data_splitter = MonthDataSplitter(
        container_upper_limit_percentage=0.1,
        train_upper_limit_percentage=0.8,
        n_months_test_sample=10,
        n_months_forward_offset=0
    )

    model_simulator = ModelSimulator(data_splitter)

    model_simulator.simulate_prediction()
    model_simulator.simulate_betting()

    print("finished")
