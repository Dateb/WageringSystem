import os
from dataclasses import dataclass
from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from datetime import datetime, timedelta

from Model.Betting.exchange_offers_parsing import RaceDateToCardMapper, BetfairHistoryDictIterator
from Model.Estimators.estimated_probabilities_creation import ProbabilityEstimates


@dataclass
class BetOffer:

    horse_name: str
    odds: float
    scratched_horses: List[str]
    event_datetime: datetime
    adjustment_factor: float

    def __str__(self) -> str:
        return f"Odds for {self.horse_name}: {self.odds}"


@dataclass
class Bet:

    race_card: RaceCard
    bet_offer: BetOffer
    stakes: float
    payout: float

    WIN_COMMISSION: float = 0.025

    def __str__(self) -> str:
        bet_str = ("-----------------------------------\n" +
                   f"Race: {self.race_card.race_id}\n" +
                   f"Offer: {self.bet_offer}\n" +
                   f"Stakes: {self.stakes}\n" +
                   f"Payout: {self.payout}\n" +
                   "-----------------------------------\n")

        return bet_str


#TODO: Separate data parsing from container functions
class BetfairOfferContainer:

    def __init__(self, test_race_cards: Dict[str, RaceCard]):
        self.test_race_cards_mapper = RaceDateToCardMapper(test_race_cards)
        self.race_offers = {}

        history_path = "../data/exchange_odds_history/Apr/"
        day_dirs = os.listdir(history_path)
        for day_dir in day_dirs:
            race_series_dirs = os.listdir(f"{history_path}/{day_dir}")
            for race_series_dir in race_series_dirs:
                history_files = os.listdir(f"{history_path}/{day_dir}/{race_series_dir}")

                for file_name in history_files:
                    if file_name.startswith("1"):
                        self.load_offers_from_race(f"{history_path}/{day_dir}/{race_series_dir}/{file_name}")

    def load_offers_from_race(self, race_history_file_path: str):
        betfair_offers = []

        history_dict_iterator = BetfairHistoryDictIterator(race_history_file_path)

        initial_history_dict = next(history_dict_iterator)

        market_definition = initial_history_dict["mc"][0]["marketDefinition"]
        scratched_horses = []

        if market_definition["marketType"] == "WIN" and market_definition["countryCode"] == "GB":
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
                    new_offers = [
                        BetOffer(
                            horse_id_to_name_map[offer_data["id"]],
                            offer_data["ltp"],
                            scratched_horses,
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
                    adjustment_factor = runner["adjustmentFactor"]
                    if adjustment_factor >= 2.5:
                        removal_datetime = datetime.strptime(runner["removalDate"][:-5], "%Y-%m-%dT%H:%M:%S")
                        adjustment_factor_lookup[runner["name"]] = {"factor": adjustment_factor, "date": removal_datetime}

            for offer in betfair_offers:
                for removed_runner in adjustment_factor_lookup.values():
                    if offer.event_datetime < removed_runner["date"]:
                        offer.adjustment_factor *= (1 - removed_runner["factor"] / 100)

            race_datetime = self.create_datetime_from_market_time(market_definition["suspendTime"])
            race_card = self.test_race_cards_mapper.get_race_card(str(race_datetime))

            if race_card is not None:
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

    def __init__(self, betfair_offer_container: BetfairOfferContainer):
        self.betfair_offer_container = betfair_offer_container

    def bet(self, probability_estimates: ProbabilityEstimates, bet_threshold: float) -> List[Bet]:
        bets = []
        already_taken_offers = {}

        for race_datetime, race_offers in self.betfair_offer_container.race_offers.items():
            race_card = self.betfair_offer_container.test_race_cards_mapper.get_race_card(race_datetime)
            if race_datetime in probability_estimates.probability_estimates:
                for offer in race_offers:
                    probability_estimate = probability_estimates.get_horse_win_probability(race_datetime, offer.horse_name, offer.scratched_horses)

                    if probability_estimate is not None:
                        offer_probability = 1 / offer.odds

                        if probability_estimate > bet_threshold * offer_probability and (race_datetime, offer.horse_name) not in already_taken_offers:
                            stakes = (offer.odds * probability_estimate - 1) / (offer.odds - 1)

                            if stakes < 0:
                                print(f"Warning, the stakes: {stakes} are negative")

                            bets.append(Bet(race_card, offer, stakes, payout=0.0))
                            already_taken_offers[(race_datetime, offer.horse_name)] = True

        return bets
