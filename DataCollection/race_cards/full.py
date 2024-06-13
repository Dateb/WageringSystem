from DataAbstraction.Present.WritableRaceCard import WritableRaceCard
from DataAbstraction.RawRaceCardInjector import RawRaceCardInjector
from DataCollection.BHA.fetch import BHAInjector
from DataCollection.Timeform.fetch import ResultTimeformFetcher, RaceCardTimeformFetcher
from DataCollection.Timeform.inject import TimeFormInjector
from DataCollection.race_cards.base import BaseRaceCardsCollector


class FullRaceCardsCollector(BaseRaceCardsCollector):

    def __init__(self, remove_non_starters: bool = True, collect_results: bool = True):
        super().__init__(remove_non_starters)
        self.collect_results = collect_results
        self.last_injection_worked = False
        if collect_results:
            self.time_form_injector = TimeFormInjector(ResultTimeformFetcher())
        else:
            self.time_form_injector = TimeFormInjector(RaceCardTimeformFetcher())

        self.bha_injector = BHAInjector()

    def create_race_card(self, race_id: str) -> WritableRaceCard:
        race_card = self.get_race_card(race_id)

        self.inject_into_race_card(race_card)

        race_card = WritableRaceCard(race_id, race_card.raw_race_card, self.remove_non_starters)

        return race_card

    def inject_into_race_card(self, race_card: WritableRaceCard) -> None:
        if (race_card.n_horses > 1 and "Arab" not in race_card.race_name and "Jebel Ali" not in race_card.race_name
                and "Shadwell" not in race_card.race_name and "Equestrian Fed. Stks" not in race_card.race_name) or race_card.country == "IE":
            try:
                self.time_form_injector.inject_time_form_attributes(race_card)
                self.last_injection_worked = True
            except:
                self.time_form_injector.time_form_collector.current_race_number -= 1
                print(f"failed injection for race: {race_card.race_id}")

                if not self.last_injection_worked:
                    print("ERROR: major mismatching between racebets and timeform source.")
                    raise Exception

                self.last_injection_worked = False

            if race_card.country == "GB" and self.collect_results:
                self.bha_injector.inject(race_card)
        else:
            print("#horses <= 1. Injection of timeform attributes is skipped.")
