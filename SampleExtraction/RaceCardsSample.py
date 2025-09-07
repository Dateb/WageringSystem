from typing import List

from pandas import DataFrame

class RaceCardsSample:

    def __init__(self, race_cards_dataframe: DataFrame, categorical_feature_names: List[str]):
        self.race_cards_dataframe = race_cards_dataframe

        for categorical_feature in categorical_feature_names:
            self.race_cards_dataframe[categorical_feature] \
                = self.race_cards_dataframe[categorical_feature].astype("category")
