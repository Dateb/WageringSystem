import pickle

from tqdm import tqdm

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.EstimatorConfiguration import EstimatorConfiguration
from Persistence.RaceCardPersistence import RaceDataPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.data_splitting import BlockSplitter


class AgentModel:
    __BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

    def __init__(self):
        bet_model_configuration = self.load_bet_model_configuration()
        self.feature_manager = FeatureManager(features=bet_model_configuration.selected_features)

        self.race_cards_loader = RaceDataPersistence("race_cards")

        model_evaluator = ModelEvaluator()
        self.race_cards_array_factory = RaceCardsArrayFactory(
            race_cards_loader=self.race_cards_loader,
            feature_manager=self.feature_manager,
            model_evaluator=model_evaluator
        )

        self.sample_columns = self.get_sample_columns()

        sample_encoder = SampleEncoder(self.feature_manager.features, self.sample_columns)

        for race_card_file_name in tqdm(self.race_cards_loader.race_data_file_names):
            race_cards = self.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            arr_of_race_cards = self.race_cards_array_factory.race_cards_to_array(race_cards)
            sample_encoder.add_race_cards_arr(arr_of_race_cards)

        race_cards_sample = sample_encoder.get_race_cards_sample()
        sample_split_generator = BlockSplitter(
            race_cards_sample,
            validation_size=0,
            validation_count=0,
        )

        train_sample = sample_split_generator.get_last_n_races_sample(bet_model_configuration.n_train_races)

        self.bet_model = bet_model_configuration.create_estimator(train_sample)

    def bet_on_race_card(self, race_card: RaceCard):
        estimation_result = self.estimate_race_card(race_card)
        betting_slips = self.bet_model.bettor.bet(estimation_result)

        return list(betting_slips.values())[0]

    def estimate_race_card(self, race_card: RaceCard):
        sample_encoder = SampleEncoder(self.feature_manager.features, self.sample_columns)
        race_card_arr = self.race_cards_array_factory.race_card_to_array(race_card)
        sample_encoder.add_race_cards_arr(race_card_arr)

        race_card_sample = sample_encoder.get_race_cards_sample()

        race_card_sample.race_cards_dataframe.to_csv(
            path_or_buf=f"../data/logs/samples/real_time_{race_card.race_id}"
        )

        estimation_result = self.bet_model.estimator.predict(race_card_sample)

        return estimation_result

    def load_bet_model_configuration(self) -> EstimatorConfiguration:
        with open(self.__BET_MODEL_CONFIGURATION_PATH, "rb") as f:
            return pickle.load(f)

    def get_sample_columns(self):
        # We load a race cards dummy list to know the columns
        dummy_race_cards = self.race_cards_loader.load_race_card_files_non_writable(
            [self.race_cards_loader.race_data_file_names[0]])
        dummy_race_cards = list(dummy_race_cards.values())
        return dummy_race_cards[0].attributes + self.feature_manager.feature_names
