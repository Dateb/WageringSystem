from typing import Dict

from Betting.Bet import Bet
from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinBetGenerator(BetGenerator):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        super().__init__(additional_ev_threshold, bet_limit)

    def add_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        sample_df = race_cards_sample.race_cards_dataframe

        odds = sample_df.loc[:, Horse.CURRENT_ODDS_KEY]
        win_probabilities = sample_df.loc[:, "win_probability"]

        sample_df.loc[:, "expected_value"] = odds * win_probabilities

        sample_df = sample_df[sample_df["expected_value"] > (1.0 + self.additional_ev_threshold)]

        kelly_numerator = sample_df.loc[:, "expected_value"] - 1
        kelly_denominator = sample_df.loc[:, Horse.CURRENT_ODDS_KEY] - 1
        sample_df["stakes_fraction"] = kelly_numerator / kelly_denominator

        sample_df["stakes"] = sample_df["stakes_fraction"] * self.bet_limit
        sample_df.loc[sample_df["stakes"] < 0.5, "stakes"] = 0.0

        for index, row in sample_df.iterrows():
            horse_id = str(int(row[Horse.HORSE_ID_KEY]))
            odds = float(row[Horse.CURRENT_ODDS_KEY])
            stakes = float(row["stakes"])
            stakes_fraction = float(row["stakes_fraction"])
            has_won = int(row[Horse.HAS_WON_KEY])
            new_bet = Bet(horse_id, odds, stakes, stakes_fraction)

            date_time = row[RaceCard.DATETIME_KEY]

            betting_slip = betting_slips[str(date_time)]
            betting_slip.add_bet(new_bet)

            if has_won:
                betting_slip.winner_id = horse_id
