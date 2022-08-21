from pandas import DataFrame


class RaceCardsSample:

    def __init__(self, race_cards_dataframe: DataFrame):
        self.race_cards_dataframe = race_cards_dataframe

        self.race_keys = list(race_cards_dataframe["date_time"].astype(str).values)
