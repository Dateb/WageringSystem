from abc import abstractmethod, ABC
from typing import List, Dict

import numpy as np
import pandas as pd

from Betting.Bet import Bet
from Betting.BettingSlip import BettingSlip, BetType
from SampleExtraction.Horse import Horse

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    def __init__(self, kelly_wealth: float):
        self._kelly_wealth = kelly_wealth

    @abstractmethod
    def bet(self, samples: pd.DataFrame) -> Dict[str, BettingSlip]:
        pass

    def _add_kelly_stakes(self, samples: pd.DataFrame) -> pd.DataFrame:
        samples.loc[:, "exp_score"] = np.exp(samples.loc[:, "score"])
        score_sums = samples.groupby([Horse.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        samples = samples.join(other=score_sums, on=Horse.RACE_ID_KEY, how="inner")
        samples.loc[:, "win_probability"] = samples.loc[:, "exp_score"] / samples.loc[:, "sum_exp_scores"]
        samples.loc[:, "expected_value"] = samples.loc[:, Horse.CURRENT_ODDS_KEY] * samples.loc[:, "win_probability"]
        samples = samples[samples["expected_value"] > 1]

        kelly_numerator = samples.loc[:, "expected_value"] - 1
        kelly_denominator = samples.loc[:, Horse.CURRENT_ODDS_KEY] - 1
        samples["kelly_fraction"] = kelly_numerator / kelly_denominator

        return samples

    def _dataframe_to_betting_slips(self, bets_df: pd.DataFrame, bet_type: BetType) -> Dict[str, BettingSlip]:
        betting_slips: Dict[str, BettingSlip] = {}
        for index, row in bets_df.iterrows():
            horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            odds = float(row[Horse.CURRENT_ODDS_KEY])
            stakes = float(row["stakes"])
            new_bet = Bet(horse_id, odds, stakes)

            race_id = str(int(row[Horse.RACE_ID_KEY]))

            if race_id not in betting_slips:
                betting_slips[race_id] = BettingSlip(race_id, bet_type)

            betting_slips[race_id].add_bet(new_bet)

        return betting_slips


