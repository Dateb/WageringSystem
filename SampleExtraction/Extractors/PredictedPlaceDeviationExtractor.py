from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PredictedPlaceDeviationExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Predicted_Place_Deviation_{self.__n_races_ago}"

    def get_value(self, horse: Horse) -> int:
        if self.__n_races_ago > horse.n_races - 1:
            return self.PLACEHOLDER_VALUE

        past_race = horse.get_race(self.__n_races_ago)
        past_horse_id = past_race.subject_to_horse_id(horse.subject_id)
        predicted_place = past_race.horse_predicted_place(past_horse_id)
        actual_place = past_race.get_place_of_horse(past_horse_id)

        return predicted_place - actual_place
