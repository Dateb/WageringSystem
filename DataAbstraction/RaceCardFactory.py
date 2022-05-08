from DataAbstraction.FormGuideFactory import FormGuideFactory
from DataAbstraction.RaceCard import RaceCard
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataCollection.Scraper import get_scraper


class RaceCardFactory:

    def __init__(self):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/races/details/id/'

    def run(self, race_id: str) -> RaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race_card = self.__scraper.request_data(api_url)

        race_card = RaceCard(race_id, raw_race_card)
        form_guide_factory = FormGuideFactory(race_id)

        form_guides = [form_guide_factory.run(subject_id) for subject_id in race_card.subject_ids]

        raw_race_card_injector = RawRaceCardInjector(race_card)
        raw_race_card_injector.inject_form_guides(form_guides)

        race_card = RaceCard(race_id, raw_race_card_injector.raw_race_card)

        return race_card
