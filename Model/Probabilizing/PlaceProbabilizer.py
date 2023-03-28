import pandas as pd
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Betting.Bets.Bet import Bet
from Model.Betting.Bets.PlaceBet import PlaceBet
from Model.Probabilizing.Probabilizer import Probabilizer
from Model.Probabilizing.place_calculation import compute_place_probabilities
from SampleExtraction.RaceCardsSample import RaceCardsSample


class PlaceProbabilizer(Probabilizer):

    def __init__(self):
        super().__init__()

    def create_betting_slips(self, race_cards_sample: RaceCardsSample, scores: ndarray):
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        race_cards_dataframe = self.set_win_probabilities(race_cards_dataframe, scores)
        race_cards_dataframe = self.set_place_probabilities(race_cards_dataframe)

        race_cards_dataframe["expected_value"] = race_cards_dataframe["place_probability"] \
                                                 * race_cards_dataframe[Horse.CURRENT_PLACE_ODDS_KEY] \
                                                 * (1 - Bet.WIN_COMMISION) - (1 + Bet.BET_TAX)

        return None

    def set_place_probabilities(self, race_cards_dataframe: pd.DataFrame) -> pd.DataFrame:
        grouped_win_information = race_cards_dataframe.groupby(RaceCard.RACE_ID_KEY)[["win_probability", RaceCard.PLACE_NUM_KEY]].agg({
            "win_probability": lambda x: list(x),
            RaceCard.PLACE_NUM_KEY: "first"
        })

        win_information = [tuple(row) for row in grouped_win_information.values]
        place_probabilities = compute_place_probabilities(win_information)

        flattened_place_probabilities = [item for sublist in place_probabilities for item in sublist]

        race_cards_dataframe["place_probability"] = flattened_place_probabilities

        return race_cards_dataframe

    def create_bet(self, horse_result: HorseResult, stakes_fraction: float) -> Bet:
        return PlaceBet([horse_result], stakes_fraction)
