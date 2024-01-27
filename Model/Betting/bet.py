from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from datetime import datetime

from Model.Betting.staking import StakesCalculator, KellyStakesCalculator, FixedStakesCalculator
from Model.Estimators.estimated_probabilities_creation import ProbabilityEstimates
from ModelTuning import simulate_conf


@dataclass
class BetOffer:

    race_card: RaceCard
    horse: Horse
    odds: float
    scratched_horses: List[str]
    event_datetime: datetime
    adjustment_factor: float

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


class Bettor(ABC):

    def __init__(self, bet_threshold: float, stakes_calculator: StakesCalculator, max_odds_thresh: float = 20.0):
        self.bet_threshold = bet_threshold
        self.stakes_calculator = stakes_calculator
        self.max_odds_thresh = max_odds_thresh

        self.already_taken_offers = {}
        self.offer_accepted_count = 0
        self.offer_rejected_count = 0

    def bet(self, offers: Dict[str, List[BetOffer]], probability_estimates: ProbabilityEstimates) -> List[Bet]:
        bets = []

        for race_datetime, race_offers in offers.items():
            if race_datetime in probability_estimates.probability_estimates:
                for bet_offer in race_offers:
                    if (
                            bet_offer.horse is not None
                            and not bet_offer.near_race_start
                            and bet_offer.odds < self.max_odds_thresh
                    ):
                        probability_estimate = probability_estimates.get_horse_win_probability(
                            race_datetime,
                            bet_offer.horse.name,
                            bet_offer.scratched_horses
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
                            self.already_taken_offers[(race_datetime, bet_offer.horse.name)] = True

        return bets

    def get_stakes_of_offer(self, bet_offer: BetOffer, probability_estimate: float, race_datetime: str) -> float:
        stakes = 0

        if probability_estimate is not None:
            if (race_datetime, bet_offer.horse.name) not in self.already_taken_offers:
                adjusted_odds = self.get_adjusted_odds(bet_offer.odds)

                if adjusted_odds > 1:
                    odds_p = 1 / adjusted_odds
                    p_residual = 1 - odds_p
                    if probability_estimate > (odds_p + self.bet_threshold * p_residual):
                        stakes = self.stakes_calculator.get_stakes(probability_estimate, adjusted_odds)
                        self.offer_accepted_count += 1
                    else:
                        self.offer_rejected_count += 1

        return stakes

    @abstractmethod
    def get_adjusted_odds(self, odds: float) -> float:
        pass

    @property
    def offer_acceptance_rate(self) -> float:
        return self.offer_accepted_count / (self.offer_accepted_count + self.offer_rejected_count)


class RacebetsBettor(Bettor):

    BET_TAX = 0.05

    def get_adjusted_odds(self, odds: float) -> float:
        return odds - self.BET_TAX


class BetfairBettor(Bettor):

    WIN_COMMISSION = 0.025

    def get_adjusted_odds(self, odds: float) -> float:
        return odds * (1 - self.WIN_COMMISSION)


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
                    stakes_calculator = FixedStakesCalculator(fixed_stakes=7.0)
                else:
                    stakes_calculator = FixedStakesCalculator(fixed_stakes=6.0)
            else:
                stakes_calculator = FixedStakesCalculator(fixed_stakes=0.5)

        if simulate_conf.MARKET_SOURCE == "Racebets":
            bettor = RacebetsBettor(bet_threshold=bet_threshold, stakes_calculator=stakes_calculator)
        else:
            bettor = BetfairBettor(bet_threshold=bet_threshold, stakes_calculator=stakes_calculator)

        return bettor

