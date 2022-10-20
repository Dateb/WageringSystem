from typing import Dict

from pandas import DataFrame

from Betting.BetGenerators.BetGenerator import BetGenerator
from Betting.Bets.Bet import Bet
from Betting.Bets.WinBet import WinBet
from Betting.BettingSlip import BettingSlip
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.HorseResult import HorseResult
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class WinBetGenerator(BetGenerator):

    def __init__(self, additional_ev_threshold: float):
        super().__init__(additional_ev_threshold)

    def add_expected_values(self, race_cards_sample: RaceCardsSample):
        sample_df = race_cards_sample.race_cards_dataframe

        sample_df.loc[:, Horse.BASE_EXPECTED_VALUE_KEY] = \
            sample_df.loc[:, Horse.CURRENT_WIN_ODDS_KEY] * sample_df.loc[:, Horse.WIN_PROBABILITY_KEY]\
            - (1 + Bet.BET_TAX)

    def add_multiple_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        self.add_expected_values(race_cards_sample)
        self.add_bets(race_cards_sample.race_cards_dataframe, betting_slips)

    def add_single_bets(self, race_cards_sample: RaceCardsSample, betting_slips: Dict[str, BettingSlip]) -> None:
        self.add_expected_values(race_cards_sample)

        sample_df = race_cards_sample.race_cards_dataframe

        max_transformed_df = sample_df.groupby([RaceCard.RACE_ID_KEY])[Horse.BASE_EXPECTED_VALUE_KEY].transform(max)
        best_ev_idx = max_transformed_df == sample_df[Horse.BASE_EXPECTED_VALUE_KEY]
        best_ev_sample_df = sample_df[best_ev_idx]
        self.add_bets(best_ev_sample_df, betting_slips)

    def add_bets(self, sample_df: DataFrame, betting_slips: Dict[str, BettingSlip]) -> None:
        sample_df = sample_df.sort_values(by=[Horse.BASE_EXPECTED_VALUE_KEY], ascending=False)

        race_date_times = list(sample_df["date_time"].astype(str).values)
        horse_numbers = sample_df.loc[:, Horse.NUMBER_KEY].values
        win_odds = sample_df.loc[:, Horse.CURRENT_WIN_ODDS_KEY].values
        place_odds = sample_df.loc[:, Horse.CURRENT_PLACE_ODDS_KEY].values
        place_num = sample_df.loc[:, RaceCard.PLACE_NUM_KEY].values
        win_probabilities = sample_df.loc[:, Horse.WIN_PROBABILITY_KEY].values
        single_ev = sample_df.loc[:, Horse.BASE_EXPECTED_VALUE_KEY].values

        for i in range(len(horse_numbers)):
            betting_slip = betting_slips[str(race_date_times[i])]
            ev = betting_slip.conditional_ev + single_ev[i]

            if ev > (0.0 + self.additional_ev_threshold):
                numerator = ev
                denominator = betting_slip.conditional_odds + win_odds[i] - (1 + Bet.BET_TAX)
                stakes_fraction = numerator / denominator

                predicted_horse_result = HorseResult(
                    number=horse_numbers[i],
                    position=1,
                    win_odds=win_odds[i],
                    place_odds=place_odds[i],
                )
                new_bet = WinBet([predicted_horse_result], stakes_fraction, win_probabilities[i])

                betting_slip.add_bet(new_bet)
