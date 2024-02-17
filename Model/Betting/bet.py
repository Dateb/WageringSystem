from abc import ABC
from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from datetime import datetime

from Model.Betting.staking import StakesCalculator, KellyStakesCalculator, FixedStakesCalculator
from Model.Estimators.estimated_probabilities_creation import EstimationResult
from ModelTuning import simulate_conf


@dataclass
class BetOffer:

    race_card: RaceCard
    horse: Horse
    odds: float
    scratched_horse_numbers: List[int]
    event_datetime: datetime
    adjustment_factor: float
    n_horses: int

    def __str__(self) -> str:
        return f"Odds for {self.horse.name}: {self.odds}"

    @property
    def minutes_until_race_start(self) -> float:
        if self.event_datetime is None:
            return 600
        return (self.race_card.datetime - self.event_datetime).seconds / 60

    @property
    def near_race_start(self) -> bool:
        return self.minutes_until_race_start < 10


@dataclass
class Bet:

    bet_offer: BetOffer
    stakes: float
    win: float
    loss: float
    probability_estimate: float
    probability_start: float

    WIN_COMMISSION: float = 0.025

    def __str__(self) -> str:
        bet_str = ("-----------------------------------\n" +
                   f"Race: {self.bet_offer.race_card.race_id}\n" +
                   f"Offer: {self.bet_offer}\n" +
                   f"Stakes: {self.stakes}\n" +
                   f"Payout: {self.payout}\n" +
                   "-----------------------------------\n")

        return bet_str

    @property
    def payout(self) -> float:
        return self.win - self.loss


class OddsVigAdjuster(ABC):

    def get_adjusted_odds(self, odds: float) -> float:
        pass


class BetfairOddsVigAdjuster(OddsVigAdjuster):

    def get_adjusted_odds(self, odds: float) -> float:
        return odds / (1 - 0.025)


class RacebetsOddsVigAdjuster(OddsVigAdjuster):

    BET_TAX = 0.05

    def get_adjusted_odds(self, odds: float) -> float:
        return odds + self.BET_TAX


class OddsThreshold:

    def __init__(self, odds_vig_adjuster: OddsVigAdjuster, alpha: float = 0.05):
        self.odds_vig_adjuster = odds_vig_adjuster
        self.alpha = alpha

    def get_min_odds(self, probability_estimate: float) -> float:
        min_odds = 1 / probability_estimate

        # Adjusting odds such that it still holds value when considering the vig:
        min_odds_with_vig = self.odds_vig_adjuster.get_adjusted_odds(min_odds)

        """"
        Use probabilistic thresholding technique to set min odds higher.

        Thresholding is used to avoid betting on tiny ev
        and possibly negative ev due to incorrect estimations.

        The equations are derived from this main inequality:

        p_est > p + bet_thresh * (1 - p)

        where
            > p_est is the estimated probability of the model
            > p is the induced probability from the odds
            > alpha is a tunable hyperparameter. A higher value will encourage more careful betting 
              and more focused betting on more favored horses, thus reducing the risk and minimizing the
              maximum drawdown.

        Setting p_est = p + alpha * (1 - p), this equation can be formulated to:

        p = (p_est - alpha) / (1 - alpha)

        The min odds needs to be converted to probabilities temporarily.
        """

        p_min_odds = 1 / min_odds_with_vig

        if (p_min_odds - self.alpha) <= 0:
            min_odds_thresh = np.inf
        else:
            p_min_odds_thresh = (p_min_odds - self.alpha) / (1 - self.alpha)
            min_odds_thresh = 1 / p_min_odds_thresh

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

        return min_odds_thresh


class Bettor:

    def __init__(
            self,
            stakes_calculator: StakesCalculator,
            odds_threshold: OddsThreshold,
            max_odds_thresh: float = 10.0,
    ):
        self.stakes_calculator = stakes_calculator
        self.odds_threshold = odds_threshold
        self.max_odds_thresh = max_odds_thresh

        self.already_taken_offers = {}
        self.offer_accepted_count = 0
        self.offer_rejected_count = 0

    def bet(self, offers: Dict[str, List[BetOffer]], estimation_result: EstimationResult) -> List[Bet]:
        bets = []

        for race_datetime, race_offers in offers.items():
            if race_datetime in estimation_result.probability_estimates:
                for bet_offer in race_offers:
                    if (
                            bet_offer.horse is not None
                            and not bet_offer.near_race_start
                    ):
                        probability_estimate = estimation_result.get_horse_win_probability(
                            race_datetime,
                            bet_offer.horse.number,
                            bet_offer.scratched_horse_numbers
                        )

                        stakes = self.get_stakes_of_offer(bet_offer, probability_estimate, race_datetime)
                        if stakes > 0.005:
                            new_bet = Bet(
                                bet_offer,
                                stakes,
                                win=0.0,
                                loss=0.0,
                                probability_estimate=probability_estimate,
                                probability_start=bet_offer.horse.sp_win_prob
                            )
                            bets.append(new_bet)
                            self.already_taken_offers[(race_datetime, bet_offer.horse.number)] = True

        return bets

    def get_stakes_of_offer(self, bet_offer: BetOffer, probability_estimate: float, race_datetime: str) -> float:
        stakes = 0

        if probability_estimate is not None:
            if (race_datetime, bet_offer.horse.number) not in self.already_taken_offers:
                min_odds = self.odds_threshold.get_min_odds(probability_estimate)
                if min_odds < bet_offer.odds and min_odds < self.max_odds_thresh:
                    stakes = self.stakes_calculator.get_stakes(probability_estimate, bet_offer.odds)
                    self.offer_accepted_count += 1
                else:
                    self.offer_rejected_count += 1

        return stakes

    @property
    def offer_acceptance_rate(self) -> float:
        return self.offer_accepted_count / (self.offer_accepted_count + self.offer_rejected_count)


class BettorFactory:

    def __init__(self):
        pass

    @staticmethod
    def create_bettor(bet_threshold: float) -> Bettor:
        if simulate_conf.STAKES_CALCULATOR == "Kelly":
            stakes_calculator = KellyStakesCalculator()
        else:
            if simulate_conf.MARKET_SOURCE == "Betfair":
                if simulate_conf.MARKET_TYPE == "WIN":
                    stakes_calculator = FixedStakesCalculator(fixed_stakes=6.0)
                else:
                    stakes_calculator = FixedStakesCalculator(fixed_stakes=6.0)
            else:
                stakes_calculator = FixedStakesCalculator(fixed_stakes=0.5)

        if simulate_conf.MARKET_SOURCE == "Betfair":
            odds_vig_adjuster = BetfairOddsVigAdjuster()
        else:
            odds_vig_adjuster = RacebetsOddsVigAdjuster()

        odds_threshold = OddsThreshold(odds_vig_adjuster, bet_threshold)
        bettor = Bettor(stakes_calculator=stakes_calculator, odds_threshold=odds_threshold)

        return bettor

