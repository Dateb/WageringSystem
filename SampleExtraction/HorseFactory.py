from typing import List

from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse
from DataCollection.PastRacesContainer import PastRacesContainer
from DataAbstraction.RaceCard import RaceCard


class HorseFactory:

    def __init__(self, feature_manager: FeatureManager):
        self.__feature_manager = feature_manager

    def create(self, race_card: RaceCard, past_races_container: PastRacesContainer) -> List[Horse]:
        horse_data = race_card.horses
        horses = [self.__create_horse(race_card, horse_id, horse_data, past_races_container) for horse_id in horse_data]

        return horses

    def __create_horse(self, race_card: RaceCard, horse_id: str, horse_data: dict, past_races_container: PastRacesContainer) -> Horse:
        race_id = race_card.race_id
        track_id = race_card.track_id
        current_odds = race_card.get_current_odds_of_horse(horse_id)
        place = self.get_place_of_horse(horse_id, horse_data)
        raw_horse_data = horse_data[horse_id]

        subject_id = race_card.get_subject_id_of_horse(horse_id)

        races = [race_card]
        if past_races_container.is_past_race_available(race_id, subject_id, n_races_ago=1):
            races.append(past_races_container.get_past_race(race_id, subject_id, 1))

        new_horse = Horse(raw_horse_data, horse_id, subject_id, race_id, track_id, current_odds, place, races)

        self.__feature_manager.set_features_of_horse(new_horse)

        return new_horse

    def get_place_of_horse(self, horse_id: str, horse_data: dict) -> int:
        horse_data = horse_data[horse_id]
        if horse_data["scratched"]:
            return -1

        if 'finalPosition' in horse_data:
            return int(horse_data["finalPosition"])

        return 100
