from typing import List

from DataAbstraction.RaceCard import RaceCard


class Horse:

    HORSE_ID_KEY: str = "horse_id"
    RACE_ID_KEY: str = "race_id"
    TRACK_ID_KEY: str = "track_id"
    PLACE_KEY: str = "place"
    RELEVANCE_KEY: str = "relevance"
    CURRENT_ODDS_KEY: str = "current_odds"
    HAS_WON_KEY: str = "has_won"
    BASE_ATTRIBUTE_NAMES: List[str] = [HORSE_ID_KEY, RACE_ID_KEY, TRACK_ID_KEY, CURRENT_ODDS_KEY, PLACE_KEY, RELEVANCE_KEY, HAS_WON_KEY]

    def __init__(self,
                 raw_data: dict,
                 horse_id: str,
                 subject_id: str,
                 race_id: str,
                 track_id: str,
                 current_odds: float,
                 place: int,
                 races: List[RaceCard],
                 ):

        self.__raw_data = raw_data
        self.__place = place
        self.__relevance = max(31 - place, 0)
        self.__has_won = 1 if place == 1 else 0
        self.__data = {
            "horse_id": horse_id,
            "race_id": race_id,
            "track_id": track_id,
            "current_odds": current_odds,
            "place": place,
            "relevance": self.__relevance,
            "has_won": self.__has_won,
        }

        self.__features = {}
        self.__races = races
        self.__subject_id = subject_id

    def set_feature(self, name: str, value):
        self.__features[name] = value

    def get_race(self, idx: int) -> RaceCard:
        return self.__races[idx]

    @property
    def attributes(self) -> List[str]:
        return self.BASE_ATTRIBUTE_NAMES + list(self.__features.keys())

    @property
    def raw_data(self) -> dict:
        return self.__raw_data

    @property
    def has_past_races(self) -> bool:
        return len(self.__races) > 1

    @property
    def n_races(self) -> int:
        return len(self.__races)

    @property
    def values(self) -> List:
        self.__data.update(self.__features)
        return list(self.__data.values())

    @property
    def horse_id(self):
        return self.__data[self.HORSE_ID_KEY]

    @property
    def subject_id(self):
        return self.__subject_id

    @property
    def race_id(self):
        return self.__data[self.RACE_ID_KEY]

    @property
    def place(self):
        return self.__place

    @property
    def current_odds(self):
        return self.__data[self.CURRENT_ODDS_KEY]

