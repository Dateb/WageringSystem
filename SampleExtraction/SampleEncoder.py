import numpy as np
import pandas as pd
from typing import List

from pandas import DataFrame
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse
from SampleExtraction.HorseFactory import HorseFactory
from DataAbstraction.RaceCard import RaceCard


class SampleEncoder:

    def __init__(self, feature_manager: FeatureManager):
        self.__feature_names = [
            feature_extractor.get_name() for feature_extractor in feature_manager.ENABLED_FEATURE_EXTRACTORS
        ]
        self.__horse_factory = HorseFactory(feature_manager)

    def transform(self, race_cards: List[RaceCard]) -> DataFrame:
        horses = []
        for race_card in race_cards:
            horses += self.__horse_factory.create(race_card)

        horse_attributes = horses[0].attributes
        runners_data = np.array([horse.values for horse in horses])
        horses_df = pd.DataFrame(data=runners_data, columns=horse_attributes)
        horses_df[self.__feature_names] = horses_df[self.__feature_names].apply(pd.to_numeric, errors="coerce")
        horses_df[Horse.RELEVANCE_KEY] = horses_df[Horse.RELEVANCE_KEY].apply(pd.to_numeric, errors="coerce")

        return horses_df
