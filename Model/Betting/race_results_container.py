from typing import Dict

from DataAbstraction.Present.RaceCard import RaceCard


class RaceResultsContainer:

    def __init__(self):
        self.race_results = {}

    def add_results_from_race_cards(self, race_cards: Dict[str, RaceCard]):
        for race_card in race_cards.values():
            self.race_results[str(race_card.datetime)] = race_card.race_result
