from typing import List

from DataAbstraction.RaceCardFactory import RaceCardFactory
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.WritableRaceCard import WritableRaceCard


class RaceCardsCollector:

    def __init__(self, remove_non_starters: bool = True):
        self.__race_card_factory = RaceCardFactory(remove_non_starters)

    def collect_final_full_race_cards_from_race_ids(self, race_ids: List[str]) -> List[RaceCard]:
        new_base_race_cards = [self.__race_card_factory.get_race_card(race_id) for race_id in race_ids]
        final_race_ids = [race_card.race_id for race_card in new_base_race_cards if race_card.is_final]
        final_full_race_cards = self.collect_full_race_cards_from_race_ids(final_race_ids)

        return final_full_race_cards

    def collect_base_race_cards_from_race_ids(self, race_ids: List[str]) -> List[WritableRaceCard]:
        counter = 0
        n_race_cards = len(race_ids)
        new_race_cards = []
        for race_id in race_ids:
            print(f"Race card: {counter}/{n_race_cards}...")
            race_card = self.__race_card_factory.get_race_card(race_id)
            new_race_cards.append(race_card)
            counter += 1

        return new_race_cards

    def collect_full_race_cards_from_race_ids(self, race_ids: List[str]) -> List[WritableRaceCard]:
        counter = 0
        n_race_cards = len(race_ids)
        new_race_cards = []
        for race_id in race_ids:
            print(race_id)
            print(f"Race card: {counter}/{n_race_cards}...")
            race_card = self.__race_card_factory.run(race_id)
            new_race_cards.append(race_card)
            counter += 1

        return new_race_cards

