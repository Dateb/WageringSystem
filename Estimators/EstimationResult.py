from pandas import DataFrame

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard


class EstimationResult:

    def __init__(self, race_cards_dataframe: DataFrame):
        self.race_keys = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        self.race_ids = list(race_cards_dataframe[RaceCard.RACE_ID_KEY])

        race_names = race_cards_dataframe[RaceCard.RACE_NAME_KEY].values
        race_date_times = list(race_cards_dataframe[RaceCard.DATETIME_KEY].astype(str).values)
        horse_names = race_cards_dataframe.loc[:, Horse.NAME_KEY].values
        horse_numbers = race_cards_dataframe.loc[:, Horse.NUMBER_KEY].values
        win_odds = race_cards_dataframe.loc[:, Horse.CURRENT_WIN_ODDS_KEY].values
        place_odds = race_cards_dataframe.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values
        win_probabilities = race_cards_dataframe.loc[:, Horse.WIN_PROBABILITY_KEY].values

        self.horse_results = [
            HorseResult(
                race_name=race_names[i],
                race_date_time=race_date_times[i],
                number=horse_numbers[i],
                name=horse_names[i],
                position=1,
                win_probability=win_probabilities[i],
                win_odds=win_odds[i],
                place_odds=place_odds[i],
            ) for i in range(len(horse_numbers))
        ]

    @property
    def json(self) -> dict:
        estimation_json = {
            "race": {
                "id": self.race_ids[0],
                "name": self.horse_results[0].race_name,
                "date_time": self.horse_results[0].race_date_time,
            },
            "horses": [
                {
                    "id": horse_result.number,
                    "name": horse_result.name,
                    "win_probability": horse_result.win_probability,
                    "min_odds": 1 / horse_result.win_probability,
                 }
                for horse_result in self.horse_results
            ]
        }

        return estimation_json
