from DataCollection.RawRaceCard import RawRaceCard
from SampleExtraction.RaceCard import RaceCard


class PastRacesContainer:

    def __init__(self, raw_past_races: dict):
        self.__raw_past_races = raw_past_races

    def get_past_race(self, race_id: str, horse_id: str, n_races_ago: int) -> RaceCard:
        past_race_key = f"(\'{race_id}\', \'{horse_id}\', {n_races_ago})"

        raw_race_data = self.__raw_past_races[past_race_key]
        past_race_id = raw_race_data["race"]["idRace"]
        raw_race_card = RawRaceCard(past_race_id, raw_race_data)
        return RaceCard(raw_race_card)

