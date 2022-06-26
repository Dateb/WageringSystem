import numpy as np
import pandas as pd
from typing import List, Tuple, Dict

from pandas import DataFrame
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse
from SampleExtraction.HorseFactory import HorseFactory
from DataAbstraction.RaceCard import RaceCard


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager, train_fraction: float = 0.8):
        self.__feature_containers = [
            feature_extractor.container for feature_extractor in feature_manager.ENABLED_FEATURE_EXTRACTORS
        ]
        self.__feature_names = [
            feature_extractor.get_name() for feature_extractor in feature_manager.ENABLED_FEATURE_EXTRACTORS
        ]
        self.__horse_factory = HorseFactory(feature_manager)
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
        for feature_container in self.__feature_containers:
            feature_container.fit(train_race_cards)

        return self.__race_cards_to_dataframe(train_race_cards)

    def __race_cards_to_dataframe(self, race_cards: List[RaceCard]) -> DataFrame:
        horses = []
        for race_card in race_cards:
            horses += self.__horse_factory.create(race_card)

        horse_attributes = horses[0].attributes
        runners_data = np.array([horse.values for horse in horses])
        horses_df = pd.DataFrame(data=runners_data, columns=horse_attributes)
        horses_df[self.__feature_names] = horses_df[self.__feature_names].apply(pd.to_numeric, errors="coerce")
        horses_df[Horse.RELEVANCE_KEY] = horses_df[Horse.RELEVANCE_KEY].apply(pd.to_numeric, errors="coerce")
        horses_df[Horse.CURRENT_ODDS_KEY] = horses_df[Horse.CURRENT_ODDS_KEY].apply(pd.to_numeric, errors="coerce")

        return horses_df
