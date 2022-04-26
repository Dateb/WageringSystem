from DataCollection.FormGuide import FormGuide
from DataCollection.Scraper import get_scraper


class FormGuideFactory:
    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/formguide/form/id/'

    def run(self, subject_id: int) -> FormGuide:
        api_url = f"{self.__base_api_url}{str(subject_id)}"
        raw_formguide_data = self.__scraper.request_data(api_url)

        return FormGuide(subject_id, raw_formguide_data)

