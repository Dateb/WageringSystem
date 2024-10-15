import pickle
import time
import pandas as pd
from wagering_utils import stream_data

from Model.Estimation.models import WinRankingEstimator
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.simulate_conf import BET_RESULT_PATH
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class FastModelSimulator:

    def __init__(self):
        self.stream_data_manager = stream_data.StreamDataManager("../data/race_cards_dev", 0.8)

        self.model_evaluator = None
        self.estimation_result = None
        self.test_race_cards = None

        self.train_sample = None
        self.validation_sample = None

        self.feature_manager = FeatureManager()
        self.feature_manager.feature_names = self.stream_data_manager.get_feature_names()
        self.feature_manager.categorical_feature_names = self.stream_data_manager.get_categorical_feature_names()

        self.estimator = WinRankingEstimator(self.feature_manager)

    def fit_estimator(self) -> None:
        start = time.time()
        dict_data = self.stream_data_manager.get_train_stream_data()
        sample_df = pd.DataFrame.from_dict(dict_data)
        sample_df = sample_df[~sample_df["is_nonrunner"]]
        end = time.time()
        print(f"Time: {end - start}")
        train_sample = RaceCardsSample(sample_df, self.feature_manager.categorical_feature_names)
        print(train_sample.race_cards_dataframe)

        train_sample.race_cards_dataframe = train_sample.race_cards_dataframe.sort_values(by="race_id")
        self.estimator.fit(train_sample)
        print("Model tuning completed!")

    def simulate_prediction(self) -> float:
        self.fit_estimator()

        start = time.time()
        test_sample = RaceCardsSample(
            pd.DataFrame.from_dict(self.stream_data_manager.get_test_stream_data()),
            self.feature_manager.categorical_feature_names
        )
        end = time.time()
        print(f"Time: {end - start}")
        test_sample.race_cards_dataframe = test_sample.race_cards_dataframe.sort_values(by="race_id")

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
    model_simulator = FastModelSimulator()

    model_simulator.simulate_prediction()
    model_simulator.simulate_betting()

    print("finished")
