from DataAbstraction.RaceCard import RaceCard


class WritableRaceCard(RaceCard):

    def __init__(self, race_id: str, raw_race_card: dict, remove_non_starters: bool):
        super().__init__(race_id, raw_race_card, remove_non_starters)
        self.__raw_race_card = raw_race_card

    @property
    def raw_race_card(self) -> dict:
        return self.__raw_race_card
