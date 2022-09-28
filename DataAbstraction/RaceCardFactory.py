from DataCollection.FormGuideFactory import FormGuideFactory
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataCollection.Scraper import get_scraper


class RaceCardFactory:

    __N_MAX_PAST_RACES_TO_INJECT: int = 2

    def __init__(self, remove_non_starters: bool = True):
        self.__scraper = get_scraper()
        self.__base_api_url = 'https://www.racebets.de/ajax/races/details/id/'
        self.__remove_non_starters = remove_non_starters

    def run(self, base_race_id: str) -> WritableRaceCard:
        race_card = self.get_race_card(base_race_id)

        form_guide_factory = FormGuideFactory(race_card.raw_race_card["race"]["idRace"])

        form_guides = [form_guide_factory.run(horse.subject_id) for horse in race_card.horses]

        raw_race_card_injector = RawRaceCardInjector(race_card)
        raw_race_card_injector.inject_win_time_to_race_card()
        raw_race_card_injector.inject_horse_distance_to_race_card(form_guides)
        raw_race_card_injector.inject_form_tables(form_guides)

        race_card = WritableRaceCard(base_race_id, raw_race_card_injector.raw_race_card, self.__remove_non_starters)

        return race_card

    def get_race_card(self, race_id: str) -> WritableRaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race_card = self.__scraper.request_data(api_url)

        if "runners" not in raw_race_card:
            return None

        return WritableRaceCard(race_id, raw_race_card, self.__remove_non_starters)
