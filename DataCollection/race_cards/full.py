from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataCollection.Timeform.fetch import ResultTimeformFetcher, RaceCardTimeformFetcher
from DataCollection.Timeform.inject import TimeFormInjector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class FullRaceCardsCollector(BaseRaceCardsCollector):

    def __init__(self, remove_non_starters: bool = True, collect_results: bool = True):
        super().__init__(remove_non_starters)
        self.collect_results = collect_results
        if collect_results:
            self.time_form_injector = TimeFormInjector(ResultTimeformFetcher())
        else:
            self.time_form_injector = TimeFormInjector(RaceCardTimeformFetcher())

    def create_race_card(self, race_id: str) -> WritableRaceCard:
        race_card = self.get_race_card(race_id)

        raw_race_card_injector = RawRaceCardInjector(race_card)

        if race_card.n_horses > 1:
            self.time_form_injector.inject_time_form_attributes(race_card)
        else:
            print("#horses <= 1. Injection of timeform attributes is skipped.")

        race_card = WritableRaceCard(race_id, raw_race_card_injector.raw_race_card, self.remove_non_starters)

        return race_card
