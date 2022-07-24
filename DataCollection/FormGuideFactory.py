from DataCollection.FormGuide import FormGuide
from DataCollection.Scraper import get_scraper


class FormGuideFactory:
    def __init__(self, race_date: int):
        self.__race_date = race_date
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/formguide/form/id/'

    def run(self, subject_id: str) -> FormGuide:
        api_url = f"{self.__base_api_url}{subject_id}"
        raw_formguide = self.__scraper.request_data(api_url)

        return FormGuide(self.__race_date, subject_id, raw_formguide)

