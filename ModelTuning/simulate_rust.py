import pickle
import time
import pandas as pd
from tqdm import tqdm
from wagering_utils import stream_data

from Model.Estimation.models import WinRankingEstimator
from ModelTuning import simulate_conf
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.simulate_conf import BET_RESULT_PATH
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.data_splitting import MonthDataSplitter


class ModelSimulator:

    def __init__(self, month_data_splitter: MonthDataSplitter):
        self.stream_data_manager = stream_data.StreamDataManager("../data/race_cards_dev", 0.8)
        self.month_data_splitter = month_data_splitter

        self.model_evaluator = None
        self.estimation_result = None
        self.test_race_cards = None

        self.train_sample = None
        self.validation_sample = None

        self.feature_manager = FeatureManager()
        self.feature_manager.feature_names = self.stream_data_manager.get_feature_names()
        self.feature_manager.categorical_feature_names = []

        # weak_estimators = [
        #     WinRankingEstimator(self.feature_manager),
        #     WinRegressionEstimator(self.feature_manager),
        #     # WinClassificationEstimator(self.feature_manager)
        # ]
        # self.estimator = AvgEstimator(self.feature_manager, weak_estimators)
        self.estimator = WinRankingEstimator(self.feature_manager)
        # self.estimator = WinRegressionEstimator(self.feature_manager)
        self.race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)

        print(f"#container months: {len(self.month_data_splitter.container_file_names)}")
        print(f"#train months: {len(self.month_data_splitter.train_file_names)}")
        print(f"#test months: {len(self.month_data_splitter.test_file_names)}")

        for race_card_file_name in tqdm(self.month_data_splitter.container_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable(
                [race_card_file_name]
            )

            self.race_cards_array_factory.race_cards_to_array(race_cards)

        # features not known from the container race card
        # DO: this throws an indexerror when containers are none
        container_race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable(
            self.month_data_splitter.container_file_names
        )
        container_race_cards = list(container_race_cards.values())
        self.columns = container_race_cards[0].attributes + self.feature_manager.feature_names

        self.sample_encoder = SampleEncoder(self.feature_manager.features, self.columns)

    def fit_estimator(self) -> None:
        start = time.time()
        dict_data = self.stream_data_manager.get_train_stream_data()
        train_sample = RaceCardsSample(pd.DataFrame.from_dict(dict_data))
        end = time.time()
        print(f"Time: {end - start}")
        print(train_sample.race_cards_dataframe)

        self.estimator.fit(train_sample)
        print("Model tuning completed!")

    def simulate_prediction(self) -> float:
        self.fit_estimator()

        start = time.time()
        test_sample = RaceCardsSample(pd.DataFrame.from_dict(self.stream_data_manager.get_test_stream_data()))
        end = time.time()
        print(f"Time: {end - start}")

        self.model_evaluator = ModelEvaluator()

        self.test_race_cards = {}

        # DO: remove saving from function
        test_sample.race_cards_dataframe.to_csv("../data/samples/test_sample.csv")

        self.estimation_result, test_loss = self.estimator.predict(test_sample)

        return test_loss

    def simulate_betting(self) -> None:
        bet_result = self.model_evaluator.get_bets_of_model(self.estimation_result, self.test_race_cards)

        print(bet_result)

        with open(BET_RESULT_PATH, "wb") as f:
            pickle.dump(bet_result, f)


if __name__ == '__main__':

    data_splitter = MonthDataSplitter(
        container_upper_limit_percentage=0.01,
        n_months_test_sample=14,
        n_months_forward_offset=0,
        race_cards_folder=simulate_conf.RELEASE_RACE_CARDS_FOLDER_NAME
    )

    model_simulator = ModelSimulator(data_splitter)

    model_simulator.simulate_prediction()
    model_simulator.simulate_betting()

    print("finished")
