import os
from dataclasses import dataclass
from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from datetime import datetime, timedelta

from Model.Betting.exchange_offers_parsing import RaceDateToCardMapper, BetfairHistoryDictIterator
from Model.Estimators.estimated_probabilities_creation import ProbabilityEstimates
from ModelTuning import simulate_conf


@dataclass
class BetOffer:

    race_card: RaceCard
    horse_name: str
    odds: float
    scratched_horses: List[str]
    event_datetime: datetime
    adjustment_factor: float

    def __str__(self) -> str:
        return f"Odds for {self.horse_name}: {self.odds}"


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


#TODO: Separate data parsing from container functions

class BetfairOfferContainer:

    def __init__(self, test_race_cards: Dict[str, RaceCard]):
        self.test_race_cards_mapper = RaceDateToCardMapper(test_race_cards)
        self.race_offers = {}

        history_path = "../data/exchange_odds_history/"

        month_dirs = os.listdir(history_path)
        for month_dir in month_dirs:
            day_dirs = os.listdir(f"{history_path}/{month_dir}")
            for day_dir in day_dirs:
                race_series_dirs = os.listdir(f"{history_path}/{month_dir}/{day_dir}")
                for race_series_dir in race_series_dirs:
                    history_files = os.listdir(f"{history_path}/{month_dir}/{day_dir}/{race_series_dir}")

                    for file_name in history_files:
                        if file_name.startswith("1"):
                            self.load_offers_from_race(f"{history_path}/{month_dir}/{day_dir}/{race_series_dir}/{file_name}")

    def load_offers_from_race(self, race_history_file_path: str):
        betfair_offers = []

        history_dict_iterator = BetfairHistoryDictIterator(race_history_file_path)

        initial_history_dict = next(history_dict_iterator)

        if initial_history_dict is None:
            print(f"failed to decode file: {race_history_file_path}")
            return

        market_definition = initial_history_dict["mc"][0]["marketDefinition"]
        scratched_horses = []

        race_datetime = self.create_datetime_from_market_time(market_definition["suspendTime"])
        race_card = self.test_race_cards_mapper.get_race_card(str(race_datetime))

        if race_card is not None:
            if market_definition["marketType"] == simulate_conf.MARKET_TYPE and market_definition["countryCode"] == "GB":
                horses = market_definition["runners"]
                horse_id_to_name_map = {runner["id"]: runner["name"] for runner in horses}

                for history_dict in history_dict_iterator:
                    unix_time_stamp = int(history_dict["pt"] / 1000)
                    event_datetime = datetime.fromtimestamp(unix_time_stamp)
                    market_condition = history_dict["mc"][0]
                    if "marketDefinition" in market_condition:
                        market_definition = history_dict["mc"][0]["marketDefinition"]
                        if "runners" in market_definition:
                            scratched_horses = self.get_scratched_horses(market_definition["runners"])

                    if "rc" in market_condition:
                        if event_datetime < race_card.datetime:
                            new_offers = [
                                BetOffer(
                                    race_card=race_card,
                                    horse_name=horse_id_to_name_map[offer_data["id"]],
                                    odds=offer_data["ltp"],
                                    scratched_horses=scratched_horses,
                                    event_datetime=event_datetime,
                                    adjustment_factor=1.0
                                )
                                for offer_data in market_condition["rc"]
                            ]
                            betfair_offers += new_offers

                adjustment_factor_lookup = {}
                final_runners = market_definition["runners"]

                for runner in final_runners:
                    if runner["status"] == "REMOVED":
                        adjustment_factor = 0.0
                        if "adjustmentFactor" in runner:
                            adjustment_factor = runner["adjustmentFactor"]
                        if adjustment_factor >= 2.5 or simulate_conf.MARKET_TYPE == "PLACE":
                            removal_datetime = datetime.strptime(runner["removalDate"][:-5], "%Y-%m-%dT%H:%M:%S")
                            adjustment_factor_lookup[runner["name"]] = {"factor": adjustment_factor, "date": removal_datetime}

                for offer in betfair_offers:
                    for removed_runner in adjustment_factor_lookup.values():
                        if offer.event_datetime < removed_runner["date"]:
                            offer.adjustment_factor *= (1 - removed_runner["factor"] / 100)

                self.race_offers[str(race_card.datetime)] = betfair_offers

    def get_scratched_horses(self, horses: dict) -> List[str]:
        scratched_horses = []
        for horse in horses:
            if horse["status"] == "REMOVED":
                scratched_horses.append(horse["name"])

        return scratched_horses

    def get_offers_from_race(self, race_key: str) -> List[BetOffer]:
        if race_key in self.race_offers:
            return self.race_offers[race_key]
        return []

    def create_datetime_from_market_time(self, market_time: str) -> datetime:
        datetime_substrings = market_time.split('T')
        date_str = datetime_substrings[0]
        time_str = datetime_substrings[1][0:5] + ":00"

        datetime_str = f"{date_str} {time_str}"

        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)


class Bettor:

    def __init__(self, bet_threshold: float):
        self.bet_threshold = bet_threshold
        self.already_taken_offers = {}

    def bet(self, offers: Dict[str, List[BetOffer]], probability_estimates: ProbabilityEstimates) -> List[Bet]:
        bets = []

        for race_datetime, race_offers in offers.items():
            if race_datetime in probability_estimates.probability_estimates:
                for bet_offer in race_offers:
                    horse = bet_offer.race_card.get_horse_by_name(bet_offer.horse_name)

                    probability_estimate = probability_estimates.get_horse_win_probability(
                        race_datetime,
                        bet_offer.horse_name,
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
                            probability_start=horse.sp_win_prob
                        )
                        bets.append(new_bet)
                        self.already_taken_offers[(race_datetime, bet_offer.horse_name)] = True

        return bets

    def get_stakes_of_offer(self, bet_offer: BetOffer, probability_estimate: float, race_datetime: str) -> float:
        stakes = 0

        if probability_estimate is not None:
            offer_probability = 1 / bet_offer.odds

            if (probability_estimate > self.bet_threshold * offer_probability
                    and (race_datetime, bet_offer.horse_name) not in self.already_taken_offers):
                stakes = (bet_offer.odds * probability_estimate - 1) / (bet_offer.odds - 1)

        return stakes
