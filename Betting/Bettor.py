from abc import abstractmethod, ABC
from typing import List

import numpy as np
import pandas as pd

from Betting.Bet import Bet, BetType
from SampleExtraction.Horse import Horse


class Bettor(ABC):

    @abstractmethod
    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        pass

    def _get_highest_n_scores(self, samples: pd.DataFrame, n: int):
        race_groups = samples.groupby([Horse.RACE_ID_KEY]).apply(
            lambda x: x.sort_values(["score"], ascending=False)
        ).reset_index(drop=True)

        return race_groups.groupby(Horse.RACE_ID_KEY).head(n)

    def _get_highest_n_expected_values(self, samples: pd.DataFrame, n: int):
        samples["exp_score"] = np.exp(samples["score"])
        score_sums = samples.groupby([Horse.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        samples = samples.join(other=score_sums, on=Horse.RACE_ID_KEY, how="inner")
        samples["win_probability"] = samples["exp_score"] / samples["sum_exp_scores"]
        samples["expected_value"] = samples["Initial_Odds"] * samples["win_probability"]
        samples["kelly_fraction"] = (samples["expected_value"] - 1) / (samples["Initial_Odds"] - 1)

        race_groups = samples.groupby([Horse.RACE_ID_KEY]).apply(
            lambda x: x.sort_values(["expected_value"], ascending=False)
        ).reset_index(drop=True)

        best_expected_values = race_groups.groupby(Horse.RACE_ID_KEY).head(n)
        positive_expected_values = best_expected_values[best_expected_values["expected_value"] > 1]
        return positive_expected_values

    def _dataframe_to_bets(self, bets_df: pd.DataFrame, bet_type: BetType) -> List[Bet]:
        print(bets_df)
        bets = []
        for index, row in bets_df.iterrows():
            race_id = str(int(row[Horse.RACE_ID_KEY]))
            bet_horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            stakes = float(row["kelly_fraction"])
            new_bet = Bet(race_id, bet_type, stakes, [bet_horse_id])
            bets.append(new_bet)

        return bets


