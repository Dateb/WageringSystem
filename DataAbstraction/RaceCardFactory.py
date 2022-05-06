from DataAbstraction.FormGuideFactory import FormGuideFactory
from DataAbstraction.RaceCard import RaceCard
from DataCollection.Scraper import get_scraper


class RaceCardFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/races/details/id/'
        self.__form_guide_factory = FormGuideFactory()

    def run(self, race_id: str) -> RaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race = self.__scraper.request_data(api_url)

        subject_ids = [raw_race["runners"]["data"][horse_id]["idSubject"] for horse_id in raw_race["runners"]["data"]]

        race_card = RaceCard(race_id, raw_race)

        return race_card
