from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.WritableHorse import WritableHorse


class WritableRaceCard(RaceCard):

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        super().__init__(race_id, raw_race_card, remove_non_starters)
        self.__raw_race_card = raw_race_card
        self.__extract_horses(raw_race_card["runners"]["data"])

    def __extract_horses(self, raw_horses: dict):
        self.horses: List[WritableHorse] = [WritableHorse(raw_horses[horse_id]) for horse_id in raw_horses]

    def get_data_of_subject(self, subject_id: str) -> dict:
        for horse in self.horses:
            if horse.subject_id == subject_id:
                return horse.raw_data

    @property
    def raw_race_card(self) -> dict:
        return self.__raw_race_card
