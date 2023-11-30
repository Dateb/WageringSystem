from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import average_place_percentile_source


class TrainerPlacePercentile(FeatureExtractor):

    average_place_percentile_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_place_percentile = average_place_percentile_source.get_average_of_name(horse.trainer_name)

        if average_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        return average_place_percentile
