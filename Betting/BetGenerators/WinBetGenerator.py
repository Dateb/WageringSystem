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

        horse_ids = sample_df.loc[:, Horse.HORSE_ID_KEY].values
        odds = sample_df.loc[:, Horse.CURRENT_ODDS_KEY].values
        win_probabilities = sample_df.loc[:, "win_probability"].values
        win_indicators = sample_df.loc[:, Horse.HAS_WON_KEY].values

        expected_values = odds * win_probabilities

        for i in range(len(horse_ids)):
            if expected_values[i] > (1.0 + self.additional_ev_threshold):
                numerator = expected_values[i] - 1
                denominator = odds[i] - 1
                stakes_fraction = numerator / denominator

                stakes = stakes_fraction * self.bet_limit

                if stakes >= 0.5:
                    new_bet = Bet(horse_ids[i], odds[i], stakes, stakes_fraction)

                    betting_slip = betting_slips[str(race_cards_sample.race_keys[i])]
                    betting_slip.add_bet(new_bet)

                    if win_indicators[i]:
                        betting_slip.winner_id = horse_ids[i]
