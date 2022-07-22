import statistics

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AveragePlaceSimilarDistanceExtractor(FeatureExtractor):

    def __init__(self, similarity_distance: int):
        self.__similarity_distance = similarity_distance
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Place_Similar_Distance_{self.__similarity_distance}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        distance_lower_bound = race_card.distance - self.__similarity_distance
        distance_upper_bound = race_card.distance + self.__similarity_distance

        places = []
        for past_race in horse.form_table.past_forms:
            if distance_lower_bound <= past_race.distance <= distance_upper_bound:
                if past_race.final_position >= 1:
                    places.append(past_race.final_position)

        if not places:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(places)
