import numpy as np
import pandas as pd
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Estimation.RaceEventProbabilities import RaceEventProbabilities
from Model.Probabilizing.Probabilizer import Probabilizer
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_event_probabilities(self, race_cards_sample: RaceCardsSample, scores: ndarray) -> RaceEventProbabilities:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe)
        race_cards_dataframe["place_probability"] = "0"

        race_cards_dataframe["expected_value"] = race_cards_dataframe[Horse.WIN_PROBABILITY_KEY] \
                                                 * race_cards_dataframe[Horse.CURRENT_WIN_ODDS_KEY] \
                                                 * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)

        return RaceEventProbabilities(race_cards_dataframe)

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="inner")

        race_cards_dataframe.loc[:, "win_probability"] = \
            race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"]

        return race_cards_dataframe
