from typing import List

from DataAbstraction.RaceCard import RaceCard


class RaceCardsFilter:

    def __init__(self):
        pass

    def filter(self, race_cards: List[RaceCard]) -> List[RaceCard]:
        return [race_card for race_card in race_cards if self.__is_accepted(race_card)]

    def __is_accepted(self, race_card: RaceCard) -> bool:
        return self.__has_three_past_races_for_every_horse(race_card)

    def __has_three_past_races_for_every_horse(self, race_card: RaceCard):
        for horse in race_card.horses:
            if len(race_card.form_table_of_horse(horse)) < 3:
                return False

        return True
