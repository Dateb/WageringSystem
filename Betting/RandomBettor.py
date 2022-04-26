import random
from typing import List

import pandas as pd

from Betting.Bet import Bet, BetType
from Betting.Bettor import Bettor
from SampleExtraction.Horse import Horse


class RandomBettor(Bettor):

    def bet(self, samples: pd.DataFrame) -> List[Bet]:
        groups = [df for _, df in samples.groupby(Horse.RACE_ID_KEY)]
        random.shuffle(groups)

        samples = pd.concat(groups).reset_index(drop=True)

        bets_df = samples.groupby(Horse.RACE_ID_KEY).head(3)

        return self._dataframe_to_bets(bets_df, bet_type=BetType.TRIFECTA)

