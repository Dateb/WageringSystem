from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataCollection.FormGuideFactory import FormGuideFactory
from DataCollection.Timeform.fetch import ResultTimeformFetcher
from DataCollection.Timeform.inject import TimeFormInjector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class FullRaceCardsCollector(BaseRaceCardsCollector):

    def __init__(self, remove_non_starters: bool = True, collect_results: bool = True):
        super().__init__(remove_non_starters)
        self.collect_results = collect_results
        self.time_form_injector = TimeFormInjector(ResultTimeformFetcher())

    def create_race_card(self, race_id: str) -> WritableRaceCard:
        race_card = self.get_race_card(race_id)

        form_guide_factory = FormGuideFactory(race_card.raw_race_card["race"]["idRace"])

        form_guides = [form_guide_factory.run(horse.subject_id) for horse in race_card.horses if horse.subject_id != 0]

        raw_race_card_injector = RawRaceCardInjector(race_card)
        if self.collect_results:
            raw_race_card_injector.inject_horse_distance_to_race_card(form_guides)
            self.time_form_injector.inject_time_form_attributes(race_card)
        raw_race_card_injector.inject_form_tables(form_guides)

        race_card = WritableRaceCard(race_id, raw_race_card_injector.raw_race_card, self.remove_non_starters)

        return race_card
