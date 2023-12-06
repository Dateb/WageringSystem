from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import average_place_percentile_source


class TrainerPlacePercentile(FeatureExtractor):

    average_place_percentile_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        place_percentile_average = average_place_percentile_source.get_average_of_name(horse.trainer_name)
        place_percentile_count = average_place_percentile_source.get_count_of_name(horse.trainer_name)

        if place_percentile_count < 10:
            return self.PLACEHOLDER_VALUE

        return place_percentile_average
