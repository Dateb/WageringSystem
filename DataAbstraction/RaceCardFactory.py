from DataCollection.FormGuideFactory import FormGuideFactory
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Scraper import get_scraper
from DataCollection.Timeform.fetch import ResultTimeformFetcher
from DataCollection.Timeform.inject import TimeFormInjector


class RaceCardFactory:

    #TODO: remove boolean flags and create proper subclasses
    def __init__(self, remove_non_starters: bool = True, collect_results: bool = True):
        self.scraper = get_scraper()
        self.base_api_url = 'https://www.racebets.de/ajax/races/details/id/'
        self.remove_non_starters = remove_non_starters
        self.collect_results = collect_results
        self.time_form_injector = TimeFormInjector(ResultTimeformFetcher())

    def run(self, base_race_id: str) -> WritableRaceCard:
        race_card = self.get_race_card(base_race_id)

        form_guide_factory = FormGuideFactory(race_card.raw_race_card["race"]["idRace"])

        form_guides = [form_guide_factory.run(horse.subject_id) for horse in race_card.horses if horse.subject_id != 0]

        raw_race_card_injector = RawRaceCardInjector(race_card)
        if self.collect_results:
            raw_race_card_injector.inject_horse_distance_to_race_card(form_guides)
            self.time_form_injector.inject_time_form_attributes(race_card)
        raw_race_card_injector.inject_form_tables(form_guides)

        race_card = WritableRaceCard(base_race_id, raw_race_card_injector.raw_race_card, self.remove_non_starters)

        return race_card

    def get_race_card(self, race_id: str) -> WritableRaceCard:
        api_url = f"{self.base_api_url}{str(race_id)}"
        raw_race_card = self.scraper.request_data(api_url)

        if "runners" not in raw_race_card:
            return None

        return WritableRaceCard(race_id, raw_race_card, self.remove_non_starters)
