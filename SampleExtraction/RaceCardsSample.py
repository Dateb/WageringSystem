from typing import List

from pandas import DataFrame

from DataAbstraction.Present.RaceCard import RaceCard


class RaceCardsSample:

    def __init__(self, race_cards_dataframe: DataFrame):
        self.race_cards_dataframe = race_cards_dataframe

        self.race_keys = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        self.race_ids = list(race_cards_dataframe[RaceCard.RACE_ID_KEY])

    @property
    def year_months(self) -> List[str]:
        return sorted(list(set(self.race_cards_dataframe["date_time"].astype(str).str[:7])))

    def get_dataframe_by_year_month(self, year_month: str):
        return self.race_cards_dataframe[self.race_cards_dataframe["date_time"].astype(str).str[:7] == year_month]
