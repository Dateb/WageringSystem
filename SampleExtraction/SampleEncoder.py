import numpy as np
import pandas as pd
from typing import List

from pandas import DataFrame

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.FeatureManager import FeatureManager
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard


class SampleEncoder:

    def __init__(self, features: List[FeatureExtractor]):
        self.__feature_names = [feature.get_name() for feature in features]

    def transform(self, race_cards: List[RaceCard]) -> DataFrame:
        samples_array = np.concatenate([race_card.to_array() for race_card in race_cards])

        race_card_attributes = race_cards[0].attributes
        samples_df = pd.DataFrame(data=samples_array, columns=race_card_attributes)
        samples_df[self.__feature_names] = samples_df[self.__feature_names].apply(pd.to_numeric, errors="coerce")
        samples_df[Horse.CURRENT_ODDS_KEY] = samples_df[Horse.CURRENT_ODDS_KEY].apply(pd.to_numeric, errors="coerce")

        return samples_df
