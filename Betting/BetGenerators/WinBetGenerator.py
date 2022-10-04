from typing import Dict

from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.Bets.Bet import Bet
from Betting.Bets.WinBet import WinBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinBetGenerator(BetGenerator):

    def __init__(self, additional_ev_threshold: float, bet_limit: float):
        super().__init__(additional_ev_threshold)

    def add_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        sample_df = race_cards_sample.race_cards_dataframe

        sample_df.loc[:, "single_ev"] = \
            sample_df.loc[:, Horse.CURRENT_WIN_ODDS_KEY] * sample_df.loc[:, "win_probability"] - (1 + Bet.BET_TAX)

        sample_df = sample_df.sort_values(by=["single_ev"], ascending=False)

        race_date_times = list(sample_df["date_time"].astype(str).values)
        horse_ids = sample_df.loc[:, Horse.HORSE_ID_KEY].values
        odds = sample_df.loc[:, Horse.CURRENT_WIN_ODDS_KEY].values
        win_probabilities = sample_df.loc[:, "win_probability"].values
        single_ev = sample_df.loc[:, "single_ev"].values

        # TODO: Remove win indicators from df
        win_indicators = sample_df.loc[:, Horse.HAS_WON_KEY].values

        for i in range(len(horse_ids)):
            betting_slip = betting_slips[str(race_date_times[i])]
            ev = betting_slip.conditional_ev + single_ev[i]

            if ev > (0.0 + self.additional_ev_threshold):
                numerator = ev
                denominator = betting_slip.conditional_odds + odds[i] - (1 + Bet.BET_TAX)
                stakes_fraction = numerator / denominator

                predicted_horse_result = HorseResult(
                    horse_id=horse_ids[i],
                    position=1,
                    win_odds=odds[i],
                    place_odds=0,
                )
                new_bet = WinBet([predicted_horse_result], stakes_fraction, win_probabilities[i])

                betting_slip.add_bet(new_bet)
