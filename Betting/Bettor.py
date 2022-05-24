from abc import abstractmethod, ABC
from typing import List

import numpy as np
import pandas as pd

from Betting.Bet import Bet, BetType
from SampleExtraction.Horse import Horse

pd.options.mode.chained_assignment = None


class Bettor(ABC):

    @abstractmethod
    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        pass

    def _get_lowest_n_odds(self, samples: pd.DataFrame, n: int):
        race_groups = samples.groupby([Horse.RACE_ID_KEY]).apply(
            lambda x: x.sort_values([Horse.CURRENT_ODDS_KEY], ascending=True)
        ).reset_index(drop=True)

        return race_groups.groupby(Horse.RACE_ID_KEY).head(n)

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

    def _dataframe_to_bets(self, bets_df: pd.DataFrame, bet_type: BetType) -> List[Bet]:
        bets = []
        for index, row in bets_df.iterrows():
            race_id = str(int(row[Horse.RACE_ID_KEY]))
            bet_horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            stakes = float(row["stakes"])
            new_bet = Bet(race_id, bet_type, stakes, [bet_horse_id])
            bets.append(new_bet)

        return bets


