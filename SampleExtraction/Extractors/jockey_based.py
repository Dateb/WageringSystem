from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import average_place_percentile_source


class JockeyPlacePercentile(FeatureExtractor):

    average_place_percentile_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_place_percentile = average_place_percentile_source.get_average_of_name(horse.jockey_name)

        if average_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        return average_place_percentile


class JockeyWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.weight == -1:
            return self.PLACEHOLDER_VALUE
        return float(horse.jockey.weight)


class WeightAllowance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.allowance == -1:
            return self.PLACEHOLDER_VALUE
        return horse.jockey.allowance
