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
        base_race_card = self.get_race_card(base_race_id)

        form_guide_factory = FormGuideFactory(base_race_id)

        form_guides = [form_guide_factory.run(horse.subject_id) for horse in base_race_card.horses]

        raw_race_card_injector = RawRaceCardInjector(base_race_card)
        raw_race_card_injector.inject_form_tables(form_guides)

        for form_guide in form_guides:
            past_race_ids = form_guide.past_race_ids
            n_past_races_to_inject = min(len(past_race_ids), self.__N_MAX_PAST_RACES_TO_INJECT)
            for i in range(n_past_races_to_inject):
                past_race_card = self.get_race_card(past_race_ids[i])

                raw_race_card_injector.inject_past_race_card(form_guide.subject_id, past_race_card)

        race_card = WritableRaceCard(base_race_id, raw_race_card_injector.raw_race_card, self.__remove_non_starters)

        return race_card

    def get_race_card(self, race_id: str) -> WritableRaceCard:
        api_url = f"{self.__base_api_url}{str(race_id)}"
        raw_race_card = self.__scraper.request_data(api_url)

        return WritableRaceCard(race_id, raw_race_card, self.__remove_non_starters)
