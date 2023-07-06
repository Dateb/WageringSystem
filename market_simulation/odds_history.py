import bz2
import json
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class BetfairOffer:

    runner_name: str
    odds: float

    def __str__(self) -> str:
        return f"Odds for {self.runner_name}: {self.odds}"


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
        runners = market_definition["runners"]
        runner_id_to_name_map = {runner["id"]: runner["name"] for runner in runners}

        for history_dict in history_dict_iterator:
            market_condition = history_dict["mc"][0]
            if "rc" in market_condition:
                new_offers = [
                    BetfairOffer(runner_id_to_name_map[offer_data["id"]], offer_data["ltp"])
                    for offer_data in market_condition["rc"]
                ]
                betfair_offers += new_offers

        track_name = market_definition["venue"]

        race_datetime = self.create_datetime_from_market_time(market_definition["marketTime"])

        race_key = f"{race_datetime}_{track_name}"

        self.race_offers[race_key] = betfair_offers

    def get_offers_from_race(self, race_datetime: datetime, track_name: str) -> List[BetfairOffer]:
        race_key = f"{race_datetime}_{track_name}"
        if race_key in self.race_offers:
            return self.race_offers[race_key]
        return []

    def create_datetime_from_market_time(self, market_time: str) -> datetime:
        datetime_substrings = market_time.split('T')
        date_str = datetime_substrings[0]
        time_str = datetime_substrings[1][0:5]

        datetime_str = f"{date_str} {time_str}"

        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")


offer_container = BetfairOfferContainer()

race_offers = offer_container.get_offers_from_race(
    race_datetime=datetime(year=2023, month=4, day=1, hour=16, minute=30),
    track_name="Chelmsford City",
)
print(race_offers)
