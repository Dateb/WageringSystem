from DataAbstraction.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper


class RaceCardFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/races/details/id/'

    def run(self, race_id: str) -> RaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race_data = self.__scraper.request_data(api_url)

        return RaceCard(race_id, raw_race_data)
