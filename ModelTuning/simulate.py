import pickle
from typing import List, Callable, Dict

from tqdm import tqdm

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimation.estimated_probabilities_creation import WinProbabilizer, PlaceProbabilizer, PlaceScoreProbabilizer
from Model.Estimation.models import BoostedTreesRanker
from ModelTuning import simulate_conf
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.simulate_conf import BET_RESULT_PATH
from Persistence.RaceCardPersistence import RaceDataPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.RaceCardsSample import RaceCardsSample
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.data_splitting import MonthDataSplitter


def load_sample(
        race_cards_array_factory: RaceCardsArrayFactory,
        sample_encoder: SampleEncoder,
        race_cards_loader: RaceDataPersistence,
        file_names: List[str],
        race_cards_save_callbacks: List[Callable[[Dict[str, RaceCard]], None]]
) -> RaceCardsSample:
    weather_persistence = RaceDataPersistence("weather")
    for race_card_file_name in tqdm(file_names):
        race_cards = race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

        for callback in race_cards_save_callbacks:
            callback(race_cards)

        weather_data = weather_persistence.load_race_data(race_card_file_name)
        for race_card in race_cards.values():
            race_card.add_weather_data(weather_data)

        arr_of_race_cards = race_cards_array_factory.race_cards_to_array(race_cards)
        sample_encoder.add_race_cards_arr(arr_of_race_cards)

    race_cards_sample = sample_encoder.get_race_cards_sample()
    race_cards_sample.race_cards_dataframe = race_cards_sample.race_cards_dataframe.sort_values(by="race_id")

    sample_encoder.delete_sample_array()

    return race_cards_sample


class ModelSimulator:

    def __init__(self, month_data_splitter: MonthDataSplitter):
        self.probabilizer = WinProbabilizer()

        self.month_data_splitter = month_data_splitter

        self.model_evaluator = None
        self.estimation_result = None
        self.test_race_cards = None

        self.train_sample = None
        self.validation_sample = None

        self.feature_manager = FeatureManager()

        gbt_ranker = BoostedTreesRanker(self.feature_manager)
        self.estimator = gbt_ranker

        self.race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager)

        print(f"#container months: {len(self.month_data_splitter.container_file_names)}")
        print(f"#train months: {len(self.month_data_splitter.train_file_names)}")
        print(f"#test months: {len(self.month_data_splitter.test_file_names)}")

        weather_persistence = RaceDataPersistence("weather")
        for race_card_file_name in tqdm(self.month_data_splitter.container_file_names):
            race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])

            weather_data = weather_persistence.load_race_data(race_card_file_name)
            for race_card in race_cards.values():
                race_card.add_weather_data(weather_data)

            self.race_cards_array_factory.race_cards_to_array(race_cards)

        # features not known from the container race card
        # TODO: this throws an indexerror when containers are none
        container_race_cards = self.month_data_splitter.race_cards_loader.load_race_card_files_non_writable(self.month_data_splitter.container_file_names)
        container_race_cards = list(container_race_cards.values())
        self.columns = container_race_cards[0].attributes + self.feature_manager.feature_names

        self.sample_encoder = SampleEncoder(self.feature_manager.features, self.columns)

    def fit_estimator(self) -> None:
        train_sample = load_sample(
            self.race_cards_array_factory,
            self.sample_encoder,
            self.month_data_splitter.race_cards_loader,
            self.month_data_splitter.train_file_names,
            race_cards_save_callbacks=[]
        )

        self.estimator.fit(train_sample)
        print("Model tuning completed!")

    def simulate_prediction(self) -> float:
        self.fit_estimator()

        test_race_cards = {}
        race_results_container = RaceResultsContainer()

        test_race_cards_array_factory = RaceCardsArrayFactory(self.feature_manager, encode_only_runners=False)

        test_sample = load_sample(
            test_race_cards_array_factory,
            self.sample_encoder,
            self.month_data_splitter.race_cards_loader,
            self.month_data_splitter.test_file_names,
            race_cards_save_callbacks=[race_results_container.add_results_from_race_cards, test_race_cards.update]
        )

        self.model_evaluator = ModelEvaluator(race_results_container)

        self.test_race_cards = {
            race_key: race_card for race_key, race_card in test_race_cards.items()
        }

        # TODO: remove saving from function
        test_sample.race_cards_dataframe.to_csv("../data/samples/test_sample.csv")

        self.estimation_result, test_loss = self.estimator.predict(test_sample)

        return test_loss

    def simulate_betting(self) -> None:
        bet_result = self.model_evaluator.get_bets_of_model(self.estimation_result, self.test_race_cards)

        with open(BET_RESULT_PATH, "wb") as f:
            pickle.dump(bet_result, f)


if __name__ == '__main__':

    data_splitter = MonthDataSplitter(
        container_upper_limit_percentage=0.1,
        n_months_test_sample=5,
        n_months_forward_offset=0,
        race_cards_folder=simulate_conf.DEV_RACE_CARDS_FOLDER_NAME
    )

    model_simulator = ModelSimulator(data_splitter)

    model_simulator.simulate_prediction()
    model_simulator.simulate_betting()

    print("finished")
