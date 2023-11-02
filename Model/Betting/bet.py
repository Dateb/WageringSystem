from dataclasses import dataclass
from typing import List, Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from datetime import datetime

from Model.Estimators.estimated_probabilities_creation import ProbabilityEstimates


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


class Bettor:

    def __init__(self, bet_threshold: float):
        self.bet_threshold = bet_threshold
        self.already_taken_offers = {}
        self.offer_accepted_count = 0
        self.offer_rejected_count = 0

    def bet(self, offers: Dict[str, List[BetOffer]], probability_estimates: ProbabilityEstimates) -> List[Bet]:
        bets = []

        for race_datetime, race_offers in offers.items():
            if race_datetime in probability_estimates.probability_estimates:
                for bet_offer in race_offers:
                    if bet_offer.horse is not None:
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
                ev = bet_offer.odds * (1 - Bet.WIN_COMMISSION) * probability_estimate

                if ev > 1 + self.bet_threshold:
                    self.offer_accepted_count += 1
                    stakes = (ev - 1) / (bet_offer.odds - 1)
                else:
                    self.offer_rejected_count += 1

        return stakes

    @property
    def offer_acceptance_rate(self) -> float:
        return self.offer_accepted_count / (self.offer_accepted_count + self.offer_rejected_count)