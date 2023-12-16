from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import average_place_percentile_source, average_momentum_source


class TrainerMomentum(FeatureExtractor):

    average_momentum_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        momentum_average = average_momentum_source.get_average_of_name(horse.trainer_name)
        momentum_count = average_momentum_source.get_count_of_name(horse.trainer_name)

        if momentum_count < 10:
            return self.PLACEHOLDER_VALUE

        return momentum_average
