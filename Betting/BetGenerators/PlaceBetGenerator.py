from typing import Dict

from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.Bets.PlaceBet import PlaceBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class PlaceBetGenerator(BetGenerator):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        super().__init__(additional_ev_threshold, bet_limit)

    def add_multiple_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        sample_df = race_cards_sample.race_cards_dataframe
        sample_df = sample_df[sample_df[RaceCard.N_HORSES_KEY] <= 7]
        sample_df = sample_df[sample_df[RaceCard.N_HORSES_KEY] >= 5]

        sample_df["place_2_prob"] = sample_df["win_probability"] / (1 - sample_df["win_probability"])
        sum_prob_df = sample_df.groupby([RaceCard.RACE_ID_KEY]).agg(prob_sum=("place_2_prob", "sum"))

        sample_df = sample_df.merge(right=sum_prob_df, how="inner", on=RaceCard.RACE_ID_KEY)
        sample_df["win_prob_complement"] = sample_df["win_probability"] * (1 - sample_df["win_probability"])
        sample_df["place_2_probability"] = sample_df["win_probability"] * (sample_df["prob_sum"] - sample_df["win_prob_complement"])
        sample_df["place_probability"] = sample_df["win_probability"] + sample_df["place_2_probability"]

        race_date_times = list(sample_df["date_time"].astype(str).values)
        horse_ids = sample_df.loc[:, Horse.HORSE_ID_KEY].values
        place_odds = sample_df.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values
        win_probabilities = sample_df.loc[:, "place_probability"].values

        expected_values = place_odds * win_probabilities

        for i in range(len(horse_ids)):
            if expected_values[i] > (1.0 + self.additional_ev_threshold):
                numerator = expected_values[i] - 1
                denominator = place_odds[i] - 1

                stakes_fraction = 0
                if denominator > 0:
                    stakes_fraction = numerator / denominator

                stakes = stakes_fraction * self.bet_limit

                if stakes >= 0.5:
                    predicted_horse_result = HorseResult(
                        horse_id=horse_ids[i],
                        position=1,
                        win_odds=0,
                        place_odds=place_odds[i],
                    )
                    new_bet = PlaceBet([predicted_horse_result], stakes)

                    betting_slip = betting_slips[str(race_date_times[i])]
                    betting_slip.add_bet(new_bet)
