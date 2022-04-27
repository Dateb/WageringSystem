from typing import List

from DataCollection.RawRaceCard import RawRaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.Horse import Horse


class RaceCard:

    def __init__(self, raw_race_card: RawRaceCard):
        self.__race_id = raw_race_card.race_id
        self.__raw_race_data = raw_race_card.raw_race_data

        self.__extract_data()

    def __extract_data(self):
        self.__event = self.__raw_race_data['event']
        self.__race = self.__raw_race_data['race']
        self.__horse_data = self.__raw_race_data['runners']['data']
        self.__result = self.__raw_race_data['result']

    def get_horses(self, feature_manager: FeatureManager) -> List[Horse]:
        horses = [self.__create_horse(horse_id, feature_manager) for horse_id in self.__horse_data]
        started_horses = [horse for horse in horses if horse.place != -1]
        return started_horses

    def __create_horse(self, horse_id: str, feature_manager: FeatureManager) -> Horse:
        starting_odds = self.get_starting_odds_of_horse(horse_id)
        place = self.get_place_of_horse(horse_id)
        raw_horse_data = self.__horse_data[horse_id]

        new_horse = Horse(raw_horse_data, horse_id, self.__race_id, self.track_id, starting_odds, place)

        feature_manager.set_features_of_horse(new_horse)

        return new_horse

    def get_starting_odds_of_horse(self, horse_id: str) -> float:
        return self.__horse_data[horse_id]["odds"]["PRC"]

    def get_place_of_horse(self, horse_id: str) -> int:
        horse_data = self.__horse_data[horse_id]
        if horse_data["scratched"]:
            return -1

        if 'finalPosition' in horse_data:
            return int(horse_data["finalPosition"])

        return len(self.runner_ids)

    def get_name_of_horse(self, horse_id: str) -> str:
        return self.__horse_data[horse_id]["name"]

    @property
    def race_id(self) -> str:
        return self.__race_id

    @property
    def track_id(self) -> str:
        return self.__event["idTrack"]

    @property
    def race(self) -> dict:
        return self.__race

    @property
    def horses(self) -> dict:
        return self.__horse_data

    @property
    def n_runners(self) -> int:
        return len(self.__horse_data)

    @property
    def runner_ids(self):
        return [horse_id for horse_id in self.__horse_data]

    @property
    def horse_names(self) -> List[str]:
        return [self.__horse_data[horse_id]['name'] for horse_id in self.__horse_data]

    @property
    def jockey_names(self) -> List[str]:
        first_names = [self.__horse_data[horse_id]['jockey']['firstName'] for horse_id in self.__horse_data]
        last_names = [self.__horse_data[horse_id]['jockey']['lastName'] for horse_id in self.__horse_data]
        return [f"{first_names[i]} {last_names[i]}" for i in range(len(first_names))]

    @property
    def trainer_names(self) -> List[str]:
        first_names = [self.__horse_data[horse_id]['trainer']['firstName'] for horse_id in self.__horse_data]
        last_names = [self.__horse_data[horse_id]['trainer']['lastName'] for horse_id in self.__horse_data]
        return [f"{first_names[i]} {last_names[i]}" for i in range(len(first_names))]

    @property
    def exacta_odds(self) -> float:
        if "other" in self.__result["odds"]:
            return float(list(self.__result["odds"]["other"][0]["EXA"].keys())[0])

        return 0.0

    @property
    def trifecta_odds(self) -> float:
        if "other" in self.__result["odds"]:
            if len(self.__result["odds"]["other"]) > 1:
                if "TRI" in self.__result["odds"]["other"][1]:
                    return float(list(self.__result["odds"]["other"][1]["TRI"].keys())[0])

        return 0.0

