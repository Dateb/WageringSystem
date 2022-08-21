import numpy as np
import pandas as pd
from typing import List

from pandas import DataFrame

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleEncoder:

    def __init__(self, features: List[FeatureExtractor]):
        self.__feature_names = [feature.get_name() for feature in features]

    def transform(self, race_cards: List[RaceCard]) -> RaceCardsSample:
        samples_array = np.concatenate([race_card.to_array() for race_card in race_cards])

        race_card_attributes = race_cards[0].attributes
        race_cards_dataframe = DataFrame(data=samples_array, columns=race_card_attributes)

        race_cards_dataframe[self.__feature_names] = \
            race_cards_dataframe[self.__feature_names].apply(pd.to_numeric, errors="coerce")

        race_cards_dataframe[Horse.CURRENT_ODDS_KEY] = \
            race_cards_dataframe[Horse.CURRENT_ODDS_KEY].apply(pd.to_numeric, errors="coerce")

        return RaceCardsSample(race_cards_dataframe)
