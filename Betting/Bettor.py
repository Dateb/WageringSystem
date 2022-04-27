from abc import abstractmethod, ABC
from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from SampleExtraction.Horse import Horse


class Bettor(ABC):

    @abstractmethod
    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        pass

    def _get_lowest_n_samples(self, samples: pd.DataFrame, n: int):
        race_groups = samples.groupby([Horse.RACE_ID_KEY]).apply(
            lambda x: x.sort_values(["score"], ascending=False)
        ).reset_index(drop=True)

        return race_groups.groupby(Horse.RACE_ID_KEY).head(n)

    def _dataframe_to_bets(self, bets_df: pd.DataFrame, bet_type: BetType) -> List[Bet]:
        bet_horses_lookup = {}
        for index, row in bets_df.iterrows():
            race_id = str(int(row[Horse.RACE_ID_KEY]))
            bet_horse_id = str(int(row[Horse.RUNNER_ID_KEY]))
            if race_id in bet_horses_lookup:
                bet_horses_lookup[race_id] += [bet_horse_id]
            else:
                bet_horses_lookup[race_id] = [bet_horse_id]

        bets = [Bet(race_id, bet_type, 1.0, bet_horses_lookup[race_id]) for race_id in bet_horses_lookup]

        return bets


