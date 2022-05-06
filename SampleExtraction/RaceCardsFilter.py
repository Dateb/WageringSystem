from datetime import date
from typing import List

from DataCollection.PastRacesContainer import PastRacesContainer
from DataAbstraction.RaceCard import RaceCard


class RaceCardsFilter:

    def __init__(self, race_cards: List[RaceCard], past_races_container: PastRacesContainer):
        self.__race_cards = race_cards
        self.__past_races_container = past_races_container

    def get_race_cards_of_day(self, day: date):
        return [race_card for race_card in self.__race_cards if race_card.date == day]

    def get_filtered_race_cards(self) -> List[RaceCard]:
        return [race_card for race_card in self.__race_cards if self.__is_accepted(race_card)]

    def __is_accepted(self, race_card: RaceCard) -> bool:
        race_id = race_card.race_id
        horses = race_card.horses

        for horse_id in horses:
            if not race_card.is_horse_scratched(horse_id):
                subject_id = race_card.get_subject_id_of_horse(horse_id)
                if not self.__past_races_container.is_past_race_computed(race_id, subject_id, 1):
                    return False

        return True

    @property
    def filtered_race_cards(self) -> List[RaceCard]:
        return self.__filtered_race_cards
