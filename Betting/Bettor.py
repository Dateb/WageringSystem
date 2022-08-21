from abc import abstractmethod, ABC
from typing import Dict
import pandas as pd

from Betting.Bet import Bet
from Betting.BettingSlip import BettingSlip, BetType
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.RaceCardsSample import RaceCardsSample

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, expected_value_additional_threshold: float, kelly_wealth: float):
        self._kelly_wealth = kelly_wealth
        self.expected_value_additional_threshold = expected_value_additional_threshold

    @abstractmethod
    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        pass

    def _add_stakes_fraction(self, samples: pd.DataFrame) -> pd.DataFrame:
        samples.loc[:, "expected_value"] = samples.loc[:, Horse.CURRENT_ODDS_KEY] * samples.loc[:, "win_probability"]
        samples = samples[samples["expected_value"] > (1.0 + self.expected_value_additional_threshold)]

        kelly_numerator = samples.loc[:, "expected_value"] - 1
        kelly_denominator = samples.loc[:, Horse.CURRENT_ODDS_KEY] - 1
        samples["stakes_fraction"] = kelly_numerator / kelly_denominator

        return samples

    def _dataframe_to_betting_slips(self, bet_race_cards_sample: RaceCardsSample, bet_type: BetType) -> Dict[str, BettingSlip]:
        bet_race_cards_dataframe = bet_race_cards_sample.race_cards_dataframe
        bet_race_cards_keys = bet_race_cards_sample.race_keys
        betting_slips: Dict[str, BettingSlip] = {
            race_key: BettingSlip("0", bet_type) for race_key in bet_race_cards_keys
        }

        for index, row in bet_race_cards_dataframe.iterrows():
            horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            odds = float(row[Horse.CURRENT_ODDS_KEY])
            stakes = float(row["stakes"])
            stakes_fraction = float(row["stakes_fraction"])
            new_bet = Bet(horse_id, odds, stakes, stakes_fraction)

            date_time = row[RaceCard.DATETIME_KEY]

            betting_slips[str(date_time)].add_bet(new_bet)

        return betting_slips


