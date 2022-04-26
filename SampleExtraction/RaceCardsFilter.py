from typing import List

from SampleExtraction.RaceCard import RaceCard


class RaceCardsFilter:

    def __init__(self, race_cards: List[RaceCard]):
        self.__filtered_race_cards = self.__get_filtered_race_cards(race_cards)

    def __get_filtered_race_cards(self, race_cards: List[RaceCard]) -> List[RaceCard]:
        return [race_card for race_card in race_cards if self.__is_accepted(race_card)]

    def __is_accepted(self, race_card: RaceCard) -> bool:
        if 0 in race_card.initial_odds:
            return False

        return True

    @property
    def filtered_race_cards(self) -> List[RaceCard]:
        return self.__filtered_race_cards
