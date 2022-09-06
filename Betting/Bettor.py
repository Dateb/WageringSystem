from abc import abstractmethod, ABC
from typing import Dict

from pandas import DataFrame

from Betting.Bet import Bet
from Betting.BettingSlip import BettingSlip, BetType
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.RaceCardsSample import RaceCardsSample
import pandas as pd

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, expected_value_additional_threshold: float, kelly_wealth: float):
        self._kelly_wealth = kelly_wealth
        self.expected_value_additional_threshold = expected_value_additional_threshold

    @abstractmethod
    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        pass

    def _add_expected_value(self, bet_dataframe: DataFrame) -> DataFrame:
        bet_dataframe.loc[:, "expected_value"] = bet_dataframe.loc[:, Horse.CURRENT_ODDS_KEY] * bet_dataframe.loc[:, "win_probability"]
        bet_dataframe = bet_dataframe[bet_dataframe["expected_value"] > (1.0 + self.expected_value_additional_threshold)]

        return bet_dataframe

    def _add_stakes_fraction(self, bet_dataframe: DataFrame) -> DataFrame:
        kelly_numerator = bet_dataframe.loc[:, "expected_value"] - 1
        kelly_denominator = bet_dataframe.loc[:, Horse.CURRENT_ODDS_KEY] - 1
        bet_dataframe["stakes_fraction"] = kelly_numerator / kelly_denominator

        return bet_dataframe

    def _dataframe_to_betting_slips(self, bet_race_cards_sample: RaceCardsSample, bet_type: BetType) -> Dict[str, BettingSlip]:
        bet_race_cards_dataframe = bet_race_cards_sample.race_cards_dataframe
        bet_race_cards_keys = bet_race_cards_sample.race_keys
        betting_slips: Dict[str, BettingSlip] = {
            race_key: BettingSlip(bet_type) for race_key in bet_race_cards_keys
        }

        for index, row in bet_race_cards_dataframe.iterrows():
            horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            odds = float(row[Horse.CURRENT_ODDS_KEY])
            stakes = float(row["stakes"])
            stakes_fraction = float(row["stakes_fraction"])
            has_won = int(row[Horse.HAS_WON_KEY])
            new_bet = Bet(horse_id, odds, stakes, stakes_fraction)

            date_time = row[RaceCard.DATETIME_KEY]

            betting_slip = betting_slips[str(date_time)]
            betting_slip.add_bet(new_bet)

            if has_won:
                betting_slip.winner_id = horse_id

        return betting_slips


