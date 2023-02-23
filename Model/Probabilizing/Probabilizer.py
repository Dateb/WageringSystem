from abc import abstractmethod, ABC

import numpy as np
import pandas as pd
from numpy import ndarray

from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Estimation.RaceEventProbabilities import RaceEventProbabilities
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Probabilizer(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def create_event_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceEventProbabilities:
        pass

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame, scores: ndarray) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return race_cards_dataframe

    @abstractmethod
    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        pass

