import numpy as np
import pandas as pd
from typing import List, Tuple, Dict

from pandas import DataFrame
from SampleExtraction.FeatureManager import FeatureManager
from DataAbstraction.Horse import Horse
from DataAbstraction.RaceCard import RaceCard


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager, train_fraction: float = 0.8):
        self.__feature_manager = feature_manager
        self.__feature_names = [
            feature_extractor.get_name() for feature_extractor in feature_manager.ENABLED_FEATURE_EXTRACTORS
        ]
        self.__train_fraction = train_fraction
        self.train_race_cards = None
        self.test_race_cards = None

    def transform(self, race_cards: Dict[str, RaceCard]) -> Tuple[DataFrame, DataFrame]:
        race_keys = list(race_cards.keys())
        race_keys.sort()

        n_races = len(race_keys)
        n_races_train = int(self.__train_fraction * n_races)

        train_race_keys = race_keys[:n_races_train]
        test_race_keys = race_keys[n_races_train:]

        self.train_race_cards = [race_cards[race_key] for race_key in train_race_keys]
        self.test_race_cards = [race_cards[race_key] for race_key in test_race_keys]

        return self.__encode_train_race_cards(self.train_race_cards), self.__race_cards_to_dataframe(self.test_race_cards)

    def __encode_train_race_cards(self, train_race_cards: List[RaceCard]) -> DataFrame:
        self.__feature_manager.fit_enabled_container(train_race_cards)

        return self.__race_cards_to_dataframe(train_race_cards)

    def __race_cards_to_dataframe(self, race_cards: List[RaceCard]) -> DataFrame:
        self.__feature_manager.set_features(race_cards)
        samples_array = np.concatenate([race_card.to_array() for race_card in race_cards])

        race_card_attributes = race_cards[0].attributes
        samples_df = pd.DataFrame(data=samples_array, columns=race_card_attributes)
        samples_df[self.__feature_names] = samples_df[self.__feature_names].apply(pd.to_numeric, errors="coerce")
        samples_df[Horse.CURRENT_ODDS_KEY] = samples_df[Horse.CURRENT_ODDS_KEY].apply(pd.to_numeric, errors="coerce")

        return samples_df
