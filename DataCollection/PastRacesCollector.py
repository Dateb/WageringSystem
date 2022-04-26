from typing import List

from DataCollection.RaceHistory import RaceHistory
from DataCollection.RawRaceCard import RawRaceCard


class PastRacesCollector:

    def __init__(self, raw_race_cards: List[RawRaceCard], race_histories: List[RaceHistory]):
        self.__samples_race_ids = [raw_race_card.race_id for raw_race_card in raw_race_cards]
        self.__race_history_ids = [race_id for race_history in race_histories for race_id in race_history.race_ids]

        self.__past_races_ids = list(set(
            [race_id for race_id in self.__race_history_ids if
             race_id not in self.__samples_race_ids]
        ))
        print(len(self.__past_races_ids))




