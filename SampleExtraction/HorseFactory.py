from typing import List

from Persistence.PastRacesPersistence import PastRacesPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse
from SampleExtraction.RaceCard import RaceCard


class HorseFactory:

    def __init__(self, feature_manager: FeatureManager):
        self.__past_races_container = PastRacesPersistence().load()
        self.__feature_manager = feature_manager

    def create(self, race_card: RaceCard) -> List[Horse]:
        horse_data = race_card.horses
        horses = [self.__create_horse(race_card, horse_id, horse_data) for horse_id in horse_data]

        return horses

    def __create_horse(self, race_card: RaceCard, horse_id: str, horse_data: dict) -> Horse:
        race_id = race_card.race_id
        track_id = race_card.track_id
        starting_odds = self.get_starting_odds_of_horse(horse_id, horse_data)
        place = self.get_place_of_horse(horse_id, horse_data)
        raw_horse_data = horse_data[horse_id]

        subject_id = race_card.get_subject_id_of_horse(horse_id)

        races = [race_card]
        if self.__past_races_container.is_past_race_available(race_id, subject_id, n_races_ago=1):
            races.append(self.__past_races_container.get_past_race(race_id, subject_id, 1))

        new_horse = Horse(raw_horse_data, horse_id, subject_id, race_id, track_id, starting_odds, place, races)

        self.__feature_manager.set_features_of_horse(new_horse)

        return new_horse

    def get_starting_odds_of_horse(self, horse_id: str, horse_data: dict) -> float:
        return horse_data[horse_id]["odds"]["PRC"]

    def get_place_of_horse(self, horse_id: str, horse_data: dict) -> int:
        horse_data = horse_data[horse_id]
        if horse_data["scratched"]:
            return -1

        if 'finalPosition' in horse_data:
            return int(horse_data["finalPosition"])

        return 100
