from typing import Dict

from Betting.BettingSlip import BettingSlip, BetType
from Betting.Bettor import Bettor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SingleKellyBettor(Bettor):

    def __init__(self, expected_value_additional_threshold: float, kelly_wealth: float):
        super().__init__(expected_value_additional_threshold, kelly_wealth)

    def bet(self, race_cards_sample: RaceCardsSample) -> Dict[str, BettingSlip]:
        bet_dataframe = race_cards_sample.race_cards_dataframe
        if "stakes_fraction" not in bet_dataframe.columns:
            bet_dataframe = self._add_expected_value(bet_dataframe)
            single_bet_idx = bet_dataframe.groupby(["date_time"])["expected_value"].transform(max) == bet_dataframe["expected_value"]
            bet_dataframe = bet_dataframe[single_bet_idx]
            self._add_stakes_fraction(bet_dataframe)

        bet_dataframe["stakes"] = bet_dataframe["stakes_fraction"] * self._kelly_wealth
        bet_dataframe.loc[bet_dataframe["stakes"] < 0.5, "stakes"] = 0.0

        return self._dataframe_to_betting_slips(RaceCardsSample(bet_dataframe), bet_type=BetType.WIN)
