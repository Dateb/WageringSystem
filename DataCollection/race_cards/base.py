from abc import abstractmethod
from typing import List

from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Scraper import get_scraper


class BaseRaceCardsCollector:

    def __init__(self, remove_non_starters: bool = True):
        self.scraper = get_scraper()
        self.base_api_url = 'https://www.racebets.de/ajax/races/details/id/'
        self.remove_non_starters = remove_non_starters

    def collect_race_cards_from_race_ids(self, race_ids: List[str]) -> List[WritableRaceCard]:
        counter = 0
        n_race_cards = len(race_ids)
        new_race_cards = []
        for race_id in race_ids:
            print(f"Race card: {counter}/{n_race_cards}...")
            race_card = self.create_race_card(race_id)
            new_race_cards.append(race_card)
            counter += 1

        return new_race_cards

    def create_race_card(self, race_id: str) -> WritableRaceCard:
        return self.get_race_card(race_id)

    def get_race_card(self, race_id: str) -> WritableRaceCard:
        api_url = f"{self.base_api_url}{str(race_id)}"
        raw_race_card = self.scraper.request_data(api_url)

        if "runners" not in raw_race_card:
            return None

        return WritableRaceCard(race_id, raw_race_card, self.remove_non_starters)
