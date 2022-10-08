from pandas import DataFrame

from DataAbstraction.Present.RaceCard import RaceCard


class RaceCardsSample:

    def __init__(self, race_cards_dataframe: DataFrame):
        self.race_cards_dataframe = race_cards_dataframe

        self.race_keys = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        self.race_ids = list(race_cards_dataframe[RaceCard.RACE_ID_KEY])
