from typing import Dict

import numpy as np

from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.Bets.ExactaBet import ExactaBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class ExactaBetGenerator(BetGenerator):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        super().__init__(additional_ev_threshold, bet_limit)

    def add_multiple_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        sample_df = race_cards_sample.race_cards_dataframe

        sample_df["place_2_prob"] = sample_df["win_probability"] / (1 - sample_df["win_probability"])
        sum_prob_df = sample_df.groupby([RaceCard.RACE_ID_KEY]).agg(prob_sum=("place_2_prob", "sum"))

        sample_df = sample_df.merge(right=sum_prob_df, how="inner", on=RaceCard.RACE_ID_KEY)
        sample_df["win_prob_complement"] = sample_df["win_probability"] * (1 - sample_df["win_probability"])
        sample_df["place_2_probability"] = sample_df["win_probability"] * (sample_df["prob_sum"] - sample_df["win_prob_complement"])

        for race_key in set(race_cards_sample.race_keys):
            race_df = sample_df[sample_df[RaceCard.DATETIME_KEY] == race_key]
            horse_ids = race_df.loc[:, Horse.NUMBER_KEY].values

            place_1_probabilities = race_df.loc[:, "win_probability"].values
            place_2_probabilities = race_df.loc[:, "place_2_prob"].values

            exacta_probabilities = np.outer(place_1_probabilities, place_2_probabilities)

            win_odds = race_df.loc[:, Horse.CURRENT_ESTIMATION_WIN_ODDS_KEY].values

            exacta_odds = np.outer(win_odds, win_odds) * 0.5
            expected_values = exacta_probabilities * exacta_odds
            for i in range(expected_values.shape[0]):
                for j in range(expected_values.shape[1]):
                    if expected_values[i][j] > (1.0 + self.additional_ev_threshold) and i != j:
                        numerator = expected_values[i][j] - 1
                        denominator = exacta_odds[i][j] - 1

                        stakes_fraction = numerator / denominator

                        stakes = stakes_fraction * self.bet_limit

                        if stakes >= 0.5:
                            place_1_prediction = HorseResult(
                                number=horse_ids[i],
                                position=1,
                                betting_odds=0,
                                place_odds=0,
                            )
                            place_2_prediction = HorseResult(
                                number=horse_ids[j],
                                position=2,
                                betting_odds=0,
                                place_odds=0,
                            )
                            new_bet = ExactaBet([place_1_prediction, place_2_prediction], stakes)

                            betting_slip = betting_slips[race_key]
                            betting_slip.add_bet(new_bet)
