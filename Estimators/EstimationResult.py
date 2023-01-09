from pandas import DataFrame

from Betting.Bets.Bet import Bet
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

        win_betting_odds = race_cards_dataframe.loc[:, Horse.CURRENT_BETTING_WIN_ODDS_KEY].values
        place_odds = race_cards_dataframe.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values

        win_probabilities = race_cards_dataframe.loc[:, Horse.WIN_PROBABILITY_KEY].values
        place_probabilities = race_cards_dataframe.loc[:, "place_probability"].values

        place_nums = race_cards_dataframe.loc[:, RaceCard.PLACE_NUM_KEY].values

        expected_values = race_cards_dataframe.loc[:, "expected_value"].values

        self.horse_results = [
            HorseResult(
                race_name=race_names[i],
                race_date_time=race_date_times[i],
                number=horse_numbers[i],
                name=horse_names[i],
                position=1,
                win_probability=win_probabilities[i],
                place_probability=place_probabilities[i],
                win_betting_odds=win_betting_odds[i],
                place_odds=place_odds[i],
                place_num=place_nums[i],
                expected_value=expected_values[i]
            ) for i in range(len(horse_numbers))
        ]

        self.horse_results = sorted(self.horse_results, key=lambda x: x.expected_value, reverse=True)
