import bz2
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class BetOffer:

    horse_name: str
    odds: float

    def __str__(self) -> str:
        return f"Odds for {self.horse_name}: {self.odds}"


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
                    return json.loads(json_string)

        raise StopIteration


class BetfairOfferContainer:

    def __init__(self):
        self.race_offers = {}

        history_path = "../data/exchange_odds_history/32228209/1.212090749.bz2"
        self.load_offers_from_race(history_path)

    def load_offers_from_race(self, race_history_file_path: str):
        betfair_offers = []

        history_dict_iterator = BetfairHistoryDictIterator(race_history_file_path)

        initial_history_dict = next(history_dict_iterator)
        print(initial_history_dict)

        market_definition = initial_history_dict["mc"][0]["marketDefinition"]
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

        track_name = market_definition["venue"]

        race_datetime = self.create_datetime_from_market_time(market_definition["marketTime"])

        race_key = f"{race_datetime}_{track_name}"
        print(race_key)

        self.race_offers[race_key] = betfair_offers

    def get_offers_from_race(self, race_datetime: datetime, track_name: str) -> List[BetOffer]:
        race_key = f"{race_datetime}_{track_name}"
        if race_key in self.race_offers:
            return self.race_offers[race_key]
        return []

    # Usage:
    # race_offers = offer_container.get_offers_from_race(
    #     race_datetime=datetime(year=2023, month=4, day=1, hour=16, minute=30),
    #     track_name="Chelmsford City",
    # )

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
        return self.probability_estimates[race_key][horse_name]


@dataclass
class Bet:

    race_key: str
    bet_offer: BetOffer
    stakes: float


def create_bets(estimation_result: EstimationResult, betfair_offer_container: BetfairOfferContainer) -> List[Bet]:
    bets = []
    already_taken_offers = {}

    for race_key, race_offers in betfair_offer_container.race_offers.items():
        for offer in race_offers:
            probability_estimate = estimation_result.get_probability_estimate(race_key, offer.horse_name)
            offer_probability = 1 / offer.odds

            if probability_estimate > offer_probability and (race_key, offer.horse_name) not in already_taken_offers:
                stakes = probability_estimate - offer_probability
                bets.append(Bet(race_key, offer, stakes))
                already_taken_offers[(race_key, offer.horse_name)] = True

    return bets


class WinOracle:

    def __init__(self, win_results: dict):
        self.win_results = win_results

    def get_payout(self, bets: List[Bet]) -> float:
        total_payout = 0

        for bet in bets:
            if bet.race_key in win_results:
                total_payout -= bet.stakes
                if self.is_winning_bet(bet):
                    total_payout += bet.stakes * bet.bet_offer.odds

        return total_payout

    def is_winning_bet(self, bet: Bet) -> bool:
        return bet.bet_offer.horse_name == self.win_results[bet.race_key]


offer_container = BetfairOfferContainer()

probability_estimates = {
    "2023-04-01 16:30:00_Chelmsford City": {
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
payout = win_oracle.get_payout(bets)

print(payout)
