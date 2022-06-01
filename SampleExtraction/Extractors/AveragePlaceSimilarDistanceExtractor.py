from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class AveragePlaceSimilarDistanceExtractor(FeatureExtractor):

    def __init__(self, similarity_distance: int):
        self.__similarity_distance = similarity_distance
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Place_Similar_Distance_{self.__similarity_distance}"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)

        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        n_past_races_of_similar_distance = 0

        distance_lower_bound = base_race_card.distance - self.__similarity_distance
        distance_upper_bound = base_race_card.distance + self.__similarity_distance

        total_place = 0
        for past_race in form_table:
            if distance_lower_bound <= past_race["raceDistance"] <= distance_upper_bound:
                if "finalPosition" in past_race:
                    n_past_races_of_similar_distance += 1
                    total_place += past_race["finalPosition"]

        if n_past_races_of_similar_distance == 0:
            return self.PLACEHOLDER_VALUE

        return total_place / n_past_races_of_similar_distance
