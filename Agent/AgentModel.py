import pickle
from typing import Dict

from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning.RankerConfigMCTS.BetModelConfiguration import BetModelConfiguration
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder

# TODO: Dict to list for race cards


class AgentModel:
    __BET_MODEL_CONFIGURATION_PATH = "../data/bet_model_configuration.dat"

    def __init__(self):
        with open(self.__BET_MODEL_CONFIGURATION_PATH, "rb") as f:
            bet_model_configuration: BetModelConfiguration = pickle.load(f)

        self.__bet_model = bet_model_configuration.create_bet_model()

        self.__feature_manager = FeatureManager(features=self.__bet_model.features)

        race_cards_loader = RaceCardsPersistence("train_race_cards")
        train_width = 17
        container_width = 4
        container_race_card_file_names = race_cards_loader.race_card_file_names[:container_width]

        self.__container_race_cards = race_cards_loader.load_race_card_files_non_writable(container_race_card_file_names)

        train_race_card_file_names = race_cards_loader.race_card_file_names[-train_width:]

        self.__train_race_cards = race_cards_loader.load_race_card_files_non_writable(train_race_card_file_names)

        self.__fit_estimator()

    def __fit_estimator(self):
        self.__feature_manager.fit_enabled_container(list(self.__container_race_cards.values()))
        self.__feature_manager.set_features(list(self.__train_race_cards.values()))

        sample_encoder = SampleEncoder(features=self.__bet_model.features)
        sample_encoder.encode_race_cards(list(self.__train_race_cards.values()))

        race_cards_sample = sample_encoder.get_race_cards_sample()

        self.__bet_model.fit_estimator(train_samples=race_cards_sample.race_cards_dataframe, validation_samples=None)

    def predict_race_card(self, race_card: RaceCard) -> Dict[str, BettingSlip]:
        self.__feature_manager.fit_enabled_container(list(self.__container_race_cards.values()))
        self.__feature_manager.set_features([race_card])

        sample_encoder = SampleEncoder(features=self.__bet_model.features)
        sample_encoder.encode_race_cards([race_card])

        next_race_sample = sample_encoder.get_race_cards_sample()

        return self.__bet_model.predict_race_cards_sample(next_race_sample)
