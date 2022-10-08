import pickle
from typing import Dict

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
        with open(self.__BET_MODEL_CONFIGURATION_PATH, "rb") as f:
            bet_model_configuration: BetModelConfiguration = pickle.load(f)

        feature_manager = FeatureManager(features=bet_model_configuration.feature_subset)

        print(bet_model_configuration.n_train_races)

        # extract training set all the way
        race_cards_loader = RaceCardsPersistence("race_cards")

        model_evaluator = ModelEvaluator()
        race_cards_array_factory = RaceCardsArrayFactory(race_cards_loader, feature_manager, model_evaluator)

        # We load a race cards dummy list to know the columns
        dummy_race_cards = race_cards_loader.load_race_card_files_non_writable(
            [race_cards_loader.race_card_file_names[0]])
        dummy_race_cards = list(dummy_race_cards.values())
        columns = dummy_race_cards[0].attributes + feature_manager.feature_names
        sample_encoder = SampleEncoder(feature_manager.features, columns)

        for race_card_file_name in tqdm([race_cards_loader.race_card_file_names[0]]):
            arr_of_race_cards = race_cards_array_factory.race_card_file_to_array(race_card_file_name)
            sample_encoder.add_race_cards_arr(arr_of_race_cards)

        race_cards_sample = sample_encoder.get_race_cards_sample()
        sample_split_generator = SampleSplitGenerator(
            race_cards_sample,
            n_train_races=bet_model_configuration.n_train_races,
            n_races_per_fold=0,
            n_folds=0,
        )

        train_sample = sample_split_generator.get_last_n_races_sample(bet_model_configuration.n_train_races)

        bet_model = bet_model_configuration.create_bet_model(train_sample)

        # estimated_race_cards_sample = bet_model.estimator.transform(race_cards_sample)
        # betting_slips = bet_model.bettor.bet(estimated_race_cards_sample)

    def __fit_estimator(self):
        self.__feature_manager.warmup_feature_sources(list(self.__container_race_cards.values()))
        self.__feature_manager.set_features(list(self.__train_race_cards.values()))

        sample_encoder = SampleEncoder(features=self.__bet_model.features)
        sample_encoder.encode_race_cards(list(self.__train_race_cards.values()))

        race_cards_sample = sample_encoder.get_race_cards_sample()

        self.__bet_model.fit_estimator(train_samples=race_cards_sample.race_cards_dataframe, validation_samples=None)

    def predict_race_card(self, race_card: RaceCard) -> Dict[str, BettingSlip]:
        self.__feature_manager.warmup_feature_sources(list(self.__container_race_cards.values()))
        self.__feature_manager.set_features([race_card])

        sample_encoder = SampleEncoder(features=self.__bet_model.features)
        sample_encoder.encode_race_cards([race_card])

        next_race_sample = sample_encoder.get_race_cards_sample()

        return self.__bet_model.predict_race_cards_sample(next_race_sample)
