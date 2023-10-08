import bz2
import json
from json import JSONDecodeError
from typing import Dict

from DataAbstraction.Present.RaceCard import RaceCard


class RaceDateToCardMapper:

    def __init__(self, race_cards: Dict[str, RaceCard]):
        self.race_cards = race_cards

    def get_race_card(self, date: str) -> RaceCard:
        if date in self.race_cards:
            return self.race_cards[date]
        return None


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
                    escaped_json_string = escaped_json_string.replace("\xa0", " ")
                    try:
                        return json.loads(escaped_json_string)
                    except JSONDecodeError:
                        return None

        raise StopIteration
