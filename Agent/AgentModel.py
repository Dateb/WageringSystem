import pickle

from tqdm import tqdm

from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsArrayFactory import RaceCardsArrayFactory
from SampleExtraction.SampleEncoder import SampleEncoder
from SampleExtraction.SampleSplitGenerator import SampleSplitGenerator


class AgentModel:
    __BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

    def __init__(self):
        bet_model_configuration = self.load_bet_model_configuration()
        self.feature_manager = FeatureManager(features=bet_model_configuration.feature_subset)

        self.race_cards_loader = RaceCardsPersistence("race_cards")

        model_evaluator = ModelEvaluator()
        self.race_cards_array_factory = RaceCardsArrayFactory(
            race_cards_loader=self.race_cards_loader,
            feature_manager=self.feature_manager,
            model_evaluator=model_evaluator
        )

        self.sample_columns = self.get_sample_columns()

        sample_encoder = SampleEncoder(self.feature_manager.features, self.sample_columns)

        n_loaded_race_cards = 0
        race_card_file_idx = 1

        # TODO: some races are missing after loading (maybe the same race gets loaded twice?)
        while n_loaded_race_cards < bet_model_configuration.n_train_races:
            race_card_file_name = self.race_cards_loader.race_card_file_names[-race_card_file_idx]
            race_cards = self.race_cards_loader.load_race_card_files_non_writable([race_card_file_name])
            arr_of_race_cards = self.race_cards_array_factory.race_cards_to_array(race_cards)
            sample_encoder.add_race_cards_arr(arr_of_race_cards)

            n_loaded_race_cards += len(race_cards)
            race_card_file_idx += 1
            print(f"Loaded {n_loaded_race_cards}/{bet_model_configuration.n_train_races} race cards.")

        race_cards_sample = sample_encoder.get_race_cards_sample()
        sample_split_generator = SampleSplitGenerator(
            race_cards_sample,
            n_races_per_fold=0,
            n_folds=0,
        )

        train_sample = sample_split_generator.get_last_n_races_sample(bet_model_configuration.n_train_races)

        self.bet_model = bet_model_configuration.create_bet_model(train_sample)

    def bet_on_race_card(self, race_card: RaceCard) -> BettingSlip:
        sample_encoder = SampleEncoder(self.feature_manager.features, self.sample_columns)
        race_card_arr = self.race_cards_array_factory.race_card_to_array(race_card)
        sample_encoder.add_race_cards_arr(race_card_arr)

        race_card_sample = sample_encoder.get_race_cards_sample()
        race_card_sample.race_cards_dataframe.to_csv(f"../data/production_race_cards/production_race_{race_card.race_id}.csv")
        betting_slips = self.bet_model.bet_on_race_cards_sample(race_card_sample)

        return betting_slips[race_card_sample.race_keys[0]]

    def load_bet_model_configuration(self) -> BetModelConfiguration:
        with open(self.__BET_MODEL_CONFIGURATION_PATH, "rb") as f:
            return pickle.load(f)

    def get_sample_columns(self):
        # We load a race cards dummy list to know the columns
        dummy_race_cards = self.race_cards_loader.load_race_card_files_non_writable(
            [self.race_cards_loader.race_card_file_names[0]])
        dummy_race_cards = list(dummy_race_cards.values())
        return dummy_race_cards[0].attributes + self.feature_manager.feature_names
