import bz2
import collections
import json
import os
from dataclasses import dataclass
from typing import List, OrderedDict
from datetime import datetime


@dataclass
class BetOffer:

    horse_name: str
    odds: float

    def __str__(self) -> str:
        return f"Odds for {self.horse_name}: {self.odds}"


@dataclass
class Bet:

    race_key: str
    bet_offer: BetOffer
    stakes: float
    payout: float

    def __str__(self) -> str:
        bet_str = ("-----------------------------------\n" +
                   f"Race: {self.race_key}\n" +
                   f"Offer: {self.bet_offer}\n" +
                   f"Stakes: {self.stakes}\n" +
                   f"Payout: {self.payout}\n" +
                   "-----------------------------------\n")

        return bet_str


class BetfairHistoryDictIterator:

    def __init__(self, betfair_history_file_path: str):
        f = bz2.open(betfair_history_file_path, "rb")
        self.raw_entries = str(f.read())

        self.json_start_idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        curly_braces_level = 0
        for i in range(self.json_start_idx, len(self.raw_entries)):
            c = self.raw_entries[i]

            if c == "{":
                curly_braces_level += 1

                if curly_braces_level == 1:
                    self.json_start_idx = i

            if c == "}":
                curly_braces_level -= 1
                if curly_braces_level == 0:
                    json_string = self.raw_entries[self.json_start_idx:i + 1]
                    self.json_start_idx = i + 1
                    escaped_json_string = json_string.translate(str.maketrans({"'":  r"\'"}))
                    return json.loads(escaped_json_string)

        raise StopIteration


class BetfairOfferContainer:

    def __init__(self):
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

        if market_definition["marketType"] == "WIN" and market_definition["countryCode"] == "GB":
            horses = market_definition["runners"]
            horse_id_to_name_map = {runner["id"]: runner["name"] for runner in horses}

            for history_dict in history_dict_iterator:
                market_condition = history_dict["mc"][0]
                if "rc" in market_condition:
                    new_offers = [
                        BetOffer(horse_id_to_name_map[offer_data["id"]], offer_data["ltp"])
                        for offer_data in market_condition["rc"]
                    ]
                    betfair_offers += new_offers

            race_datetime = self.create_datetime_from_market_time(market_definition["suspendTime"])

            race_key = create_race_key(race_datetime, market_definition["venue"])

            self.race_offers[race_key] = betfair_offers

    def get_offers_from_race(self, race_key: str) -> List[BetOffer]:
        if race_key in self.race_offers:
            return self.race_offers[race_key]
        return []

    def create_datetime_from_market_time(self, market_time: str) -> datetime:
        datetime_substrings = market_time.split('T')
        date_str = datetime_substrings[0]
        time_str = datetime_substrings[1][0:5]

        datetime_str = f"{date_str} {time_str}"

        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")


class EstimationResult:

    def __init__(self, probability_estimates: dict):
        self.probability_estimates = probability_estimates

    def get_probability_estimate(self, race_key: str, horse_name: str) -> float:
        if horse_name.upper() in self.probability_estimates[race_key]:
            return self.probability_estimates[race_key][horse_name.upper()]


def create_bets(estimation_result: EstimationResult, betfair_offer_container: BetfairOfferContainer, bet_threshold: float) -> List[Bet]:
    bets = []
    already_taken_offers = {}

    for race_key, race_offers in betfair_offer_container.race_offers.items():
        if race_key in estimation_result.probability_estimates:
            for offer in race_offers:
                probability_estimate = estimation_result.get_probability_estimate(race_key, offer.horse_name)

                if probability_estimate is not None:
                    offer_probability = 1 / offer.odds

                    if probability_estimate > bet_threshold * offer_probability and (race_key, offer.horse_name) not in already_taken_offers:
                        stakes = (offer.odds * probability_estimate - 1) / (offer.odds - 1)

                        if stakes < 0:
                            print(f"Warning, the stakes: {stakes} are negative")

                        bets.append(Bet(race_key, offer, stakes, payout=0.0))
                        already_taken_offers[(race_key, offer.horse_name)] = True

    return bets


class WinOracle:

    def __init__(self, win_results: dict):
        self.win_results = win_results

    def insert_payouts_into_bets(self, bets: List[Bet]) -> None:
        for bet in bets:
            if bet.race_key in self.win_results:
                if bet.bet_offer.horse_name.upper() in self.win_results[bet.race_key]:
                    bet.payout -= bet.stakes

                    if self.is_winning_bet(bet):
                        bet.payout += bet.stakes * bet.bet_offer.odds

    def is_winning_bet(self, bet: Bet) -> bool:
        return self.win_results[bet.race_key][bet.bet_offer.horse_name.upper()]


def create_race_key(race_datetime: datetime, track_name: str) -> str:
    if track_name == "Chelmsford":
        track_name = "Chelmsford City"
    return f"{race_datetime}_{track_name}"


def main():
    offer_container = BetfairOfferContainer()

    race_datetime = datetime(year=2023, month=4, day=1, hour=16, minute=30)
    track_name = "Chelmsford City"

    probability_estimates = {
        create_race_key(race_datetime, track_name): {
            "Valorant": 0.5,
            "Vitralite": 0.2,
            "Ostilio": 0.15,
            "Brazen Arrow": 0.1,
            "Butterfly Island": 0.03,
            "Okeanos": 0.02,
        }
    }

    estimation_result = EstimationResult(probability_estimates)
    bets = create_bets(estimation_result, offer_container)

    win_results = {
        "2023-04-01 16:30:00_Chelmsford City": "Valorant"
    }
    win_oracle = WinOracle(win_results)
    payout = win_oracle.insert_payouts_into_bets(bets)

    print(payout)


if __name__ == '__main__':
    main()
    print("finished")
