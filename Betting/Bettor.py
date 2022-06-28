from abc import abstractmethod, ABC
from typing import Dict, List
import pandas as pd

from Betting.Bet import Bet
from Betting.BettingSlip import BettingSlip, BetType
from DataAbstraction.RaceCard import RaceCard
from DataAbstraction.Horse import Horse

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, race_cards: List[RaceCard], start_kelly_wealth: float):
        self.__race_cards = race_cards
        self._start_kelly_wealth = start_kelly_wealth

    @abstractmethod
    def bet(self, samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        pass

    def _add_stakes_fraction(self, samples: pd.DataFrame) -> pd.DataFrame:
        samples.loc[:, "expected_value"] = samples.loc[:, Horse.CURRENT_ODDS_KEY] * samples.loc[:, "win_probability"]
        samples = samples[samples["expected_value"] > 1.0]

        kelly_numerator = samples.loc[:, "expected_value"] - 1
        kelly_denominator = samples.loc[:, Horse.CURRENT_ODDS_KEY] - 1
        samples["stakes_fraction"] = kelly_numerator / kelly_denominator

        return samples

    def _dataframe_to_betting_slips(self, bets_df: pd.DataFrame, bet_type: BetType) -> Dict[str, BettingSlip]:
        betting_slips: Dict[str, BettingSlip] = {
            race_card.datetime: BettingSlip(race_card, bet_type) for race_card in self.__race_cards
        }

        for index, row in bets_df.iterrows():
            horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            odds = float(row[Horse.CURRENT_ODDS_KEY])
            stakes = float(row["stakes"])
            stakes_fraction = float(row["stakes_fraction"])
            new_bet = Bet(horse_id, odds, stakes, stakes_fraction)

            date = row[RaceCard.DATETIME_KEY]
            betting_slips[date].add_bet(new_bet)

        return betting_slips


