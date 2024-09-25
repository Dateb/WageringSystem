import random
from abc import ABC
from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from DataAbstraction.Present.Horse import Horse
from datetime import datetime

from Model.Betting.race_results_container import RaceResultsContainer
from Model.Estimation.estimated_probabilities_creation import EstimationResult
from util.stats_calculator import get_max_draw_down


def bet_max_drawdown(returns):
    """
    Calculate the maximum drawdown in terms of absolute returns.

    Parameters:
    returns (list or numpy array): A list or array of returns.

    Returns:
    max_drawdown_abs (float): The maximum drawdown in absolute terms.
    """
    # Cumulative returns
    cumulative_returns = np.cumsum(returns)

    # Track running maximum
    running_max = np.maximum.accumulate(cumulative_returns)

    # Drawdown is the difference between the running maximum and the current cumulative returns
    drawdowns = running_max - cumulative_returns

    # Maximum drawdown (absolute)
    max_drawdown_abs = np.max(drawdowns)

    return max_drawdown_abs

def get_clv(starting_odds: float, offer_odds: float, adjustment_factor: float = 1.0) -> float:
    adjusted_offer_odds = offer_odds * adjustment_factor
    offer_p = 1 / adjusted_offer_odds
    starting_p = 1 / BetfairOddsVigAdjuster().get_adjusted_odds(starting_odds)
    return (starting_p - offer_p) / offer_p

class OddsVigAdjuster(ABC):

    def get_adjusted_odds(self, odds: float) -> float:
        pass


class BetfairOddsVigAdjuster(OddsVigAdjuster):

    def get_adjusted_odds(self, odds: float) -> float:
        return odds / (1 - 0.03)


@dataclass
class LiveResult:
    offer_odds: float
    starting_odds: float
    has_won: bool
    win: float
    loss: float
    adjustment_factor: float = 1.0
    stakes: float = 6.0

    @property
    def clv(self) -> float:
        if self.starting_odds > 0:
            return get_clv(self.starting_odds, self.offer_odds, self.adjustment_factor)
        return 0

    @property
    def profit(self) -> float:
        return self.win - self.loss


@dataclass
class BetOffer:

    is_success: bool
    country: str
    race_class: str
    horse_number: int
    live_result: LiveResult
    scratched_horse_numbers: List[int]
    race_datetime: datetime
    offer_datetime: datetime
    n_horses: int
    n_winners: int

    def __str__(self) -> str:
        return f"Odds for {self.horse_number}: {self.live_result.offer_odds}"

    @property
    def minutes_until_race_start(self) -> float:
        minutes_diff = (self.race_datetime - self.offer_datetime).seconds / 60

        if self.offer_datetime < self.race_datetime:
            minutes_diff *= -1
        return minutes_diff

    @property
    def near_race_start(self) -> bool:
        return self.minutes_until_race_start >= -10


@dataclass
class Bet:

    bet_offer: BetOffer
    stakes: float
    probability_estimate: float
    min_odds: float

    WIN_COMMISSION: float = 0.03

    def __str__(self) -> str:
        bet_str = ("-----------------------------------\n" +
                   f"Offer: {self.bet_offer}\n" +
                   f"Stakes: {self.stakes}\n" +
                   "-----------------------------------\n")

        return bet_str

    def set_stakes(self, stakes: float) -> None:
        self.stakes = stakes
        self.bet_offer.live_result.loss = stakes
        if self.bet_offer.is_success:
            self.bet_offer.live_result.win = self.stakes * self.bet_offer.live_result.offer_odds * self.bet_offer.live_result.adjustment_factor

    @property
    def estimated_ev(self) -> float:
        offer_odds = self.bet_offer.live_result.offer_odds
        adjusted_odds = offer_odds * (1 - self.WIN_COMMISSION)

        return self.probability_estimate * adjusted_odds

    @property
    def kelly_fraction(self) -> float:
        offer_odds = self.bet_offer.live_result.offer_odds
        adjusted_odds = offer_odds * (1 - self.WIN_COMMISSION)

        return (self.probability_estimate * adjusted_odds - 1) / (adjusted_odds - 1)


class BetResult:

    def __init__(self, bets: List[Bet], race_results_container: RaceResultsContainer):
        self.bets = bets

        self.filter_bets_without_race_result(race_results_container)
        self.filter_bets_with_nonrunner_horse(race_results_container)

    def filter_bets_without_race_result(self, race_results_container: RaceResultsContainer) -> None:
        self.bets = [bet for bet in self.bets if str(bet.bet_offer.race_datetime) in race_results_container.race_results]

    def filter_bets_with_nonrunner_horse(self, race_results_container: RaceResultsContainer) -> None:
        self.bets = [bet for bet in self.bets if not self.bet_contains_nonrunner(bet, race_results_container)]

    def bet_contains_nonrunner(self, bet: Bet, race_results_container: RaceResultsContainer) -> bool:
        race_result = race_results_container.race_results[str(bet.bet_offer.race_datetime)]
        return race_result.is_non_runner(bet.bet_offer.horse_number)

    @property
    def max_drawdown(self) -> float:
        max_drawdowns = []
        for _ in range(100):
            bets_sample = random.sample(self.bets, k=len(self.bets))

            max_draw_down = get_max_draw_down([bet.bet_offer.live_result.profit for bet in bets_sample])

            max_drawdowns.append(max_draw_down)

        return np.percentile(max_drawdowns, 95)


class OddsThreshold:

    def __init__(self, odds_vig_adjuster: OddsVigAdjuster, min_ev: float = 1.0):
        self.odds_vig_adjuster = odds_vig_adjuster
        self.min_ev = min_ev

    def get_min_odds(self, probability_estimate: float) -> float:
        min_odds = self.min_ev / probability_estimate

        # Adjusting odds such that it still holds value when considering the vig:
        min_odds_thresh = self.odds_vig_adjuster.get_adjusted_odds(min_odds)

        increments = 0.01
        if 1 <= min_odds_thresh <= 2:
            increments = 0.01
        if 2 <= min_odds_thresh <= 3:
            increments = 0.02
        if 3 <= min_odds_thresh <= 4:
            increments = 0.05
        if 4 <= min_odds_thresh <= 6:
            increments = 0.1
        if 6 <= min_odds_thresh <= 10:
            increments = 0.2
        if 10 <= min_odds_thresh <= 20:
            increments = 0.5
        if 20 <= min_odds_thresh <= 30:
            increments = 1
        if 30 <= min_odds_thresh <= 50:
            increments = 2
        if 50 <= min_odds_thresh <= 100:
            increments = 5
        if 100 <= min_odds_thresh <= 1000:
            increments = 10

        min_odds_thresh = round(min_odds_thresh / increments) * increments

        return round(min_odds_thresh, 2)


class Bettor:

    def __init__(
            self,
            odds_threshold: OddsThreshold,
            max_odds_estimation: float = 3.5,
            max_odds_offer_multiplier: float = 20,
    ):
        self.odds_threshold = odds_threshold
        self.max_odds_estimation = max_odds_estimation
        self.max_odds_offer_multiplier = max_odds_offer_multiplier

        self.already_taken_offers = {}
        self.offer_accepted_count = 0
        self.offer_rejected_count = 0

    def bet(self, offers: Dict[str, List[BetOffer]], estimation_result: EstimationResult) -> List[Bet]:
        bets = []

        for race_datetime, race_offers in offers.items():
            if race_datetime in estimation_result.probability_estimates:
                for bet_offer in race_offers:
                    if 7 <= bet_offer.offer_datetime.hour <= 10:
                        # probability_estimate = estimation_result.get_horse_win_probability(
                        #     race_datetime,
                        #     bet_offer.horse_number,
                        #     bet_offer.scratched_horse_numbers,
                        #     bet_offer.n_winners,
                        # )

                        race_probability_estimates = estimation_result.probability_estimates[race_datetime]
                        probability_estimate = None
                        if bet_offer.horse_number in race_probability_estimates:
                            probability_estimate = race_probability_estimates[bet_offer.horse_number]
                        else:
                            print(f'Bet offer: {race_datetime}/{bet_offer.horse_number} not estimated')

                        if probability_estimate is not None:
                            if (race_datetime, bet_offer.horse_number) not in self.already_taken_offers:
                                min_odds = self.odds_threshold.get_min_odds(probability_estimate)
                                max_odds_offer = min_odds * self.max_odds_offer_multiplier
                                if min_odds < bet_offer.live_result.offer_odds < max_odds_offer:
                                    new_bet = Bet(
                                        bet_offer,
                                        stakes=0.0,
                                        probability_estimate=probability_estimate,
                                        min_odds = min_odds,
                                    )
                                    bets.append(new_bet)
                                    self.offer_accepted_count += 1
                                else:
                                    self.offer_rejected_count += 1
                        self.already_taken_offers[(race_datetime, bet_offer.horse_number)] = True

        return bets

    @property
    def offer_acceptance_rate(self) -> float:
        return self.offer_accepted_count / (self.offer_accepted_count + self.offer_rejected_count)


class BettorFactory:

    def __init__(self):
        pass

    @staticmethod
    def create_bettor(min_ev: float) -> Bettor:
        odds_vig_adjuster = BetfairOddsVigAdjuster()

        odds_threshold = OddsThreshold(odds_vig_adjuster, min_ev)
        bettor = Bettor(odds_threshold=odds_threshold)

        return bettor

