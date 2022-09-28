import statistics

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Sources import SpeedFiguresSource


class AverageSpeedSimilarDistanceExtractor(FeatureExtractor):

    def __init__(self, similarity_distance: int):
        super().__init__()
        self.__similarity_distance = similarity_distance
        self.source = SpeedFiguresSource.get_feature_source()

    def get_name(self) -> str:
        return f"Average_Speed_Similar_Distance_{self.__similarity_distance}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        distance_lower_bound = race_card.distance - self.__similarity_distance
        distance_upper_bound = race_card.distance + self.__similarity_distance

        speed_figures = []
        for past_form in horse.form_table.past_forms:
            if distance_lower_bound <= past_form.distance <= distance_upper_bound:
                past_speed = self.source.__get_speed_figure(past_form)
                if past_speed != -1:
                    speed_figures.append(past_speed)

        if not speed_figures:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(speed_figures)
