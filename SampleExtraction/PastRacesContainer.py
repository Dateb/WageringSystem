from DataCollection.RawRaceCard import RawRaceCard
from SampleExtraction.RaceCard import RaceCard


class PastRacesContainer:

    def __init__(self, raw_past_races: dict):
        self.__raw_past_races = raw_past_races

    def get_past_race(self, race_id: str, subject_id: str, n_races_ago: int) -> RaceCard:
        past_race_key = f"(\'{race_id}\', {subject_id}, {n_races_ago})"
        raw_race_data = self.__raw_past_races[past_race_key]
        raw_race_card = RawRaceCard(race_id, raw_race_data)

        return RaceCard(raw_race_card)

    def is_past_race_computed(self, race_id: str, subject_id: str, n_races_ago: int) -> bool:
        past_race_key = f"(\'{race_id}\', {subject_id}, {n_races_ago})"
        return past_race_key in self.__raw_past_races

    def is_past_race_available(self, race_id: str, subject_id: str, n_races_ago: int) -> bool:
        past_race_key = f"(\'{race_id}\', {subject_id}, {n_races_ago})"
        if "ERROR" in self.__raw_past_races[past_race_key]:
            return False

        return True

    @property
    def raw_past_races(self):
        return self.__raw_past_races

