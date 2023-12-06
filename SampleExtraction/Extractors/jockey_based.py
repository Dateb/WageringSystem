from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.average_based import AverageJockeyWeightSource
from SampleExtraction.feature_sources.init import average_place_percentile_source, FEATURE_SOURCES


class JockeyPlacePercentile(FeatureExtractor):

    average_place_percentile_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        place_percentile_average = average_place_percentile_source.get_average_of_name(horse.jockey_name)
        place_percentile_count = average_place_percentile_source.get_count_of_name(horse.jockey_name)

        if place_percentile_count < 10:
            return self.PLACEHOLDER_VALUE

        return place_percentile_average


class CurrentJockeyWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.weight == -1:
            return self.PLACEHOLDER_VALUE
        return float(horse.jockey.weight)


class JockeyWeight(FeatureExtractor):

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.jockey_weight_source = AverageJockeyWeightSource(window_size)
        self.jockey_weight_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.jockey_weight_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        jockey_weight = self.jockey_weight_source.get_average_of_name(str(horse.subject_id))

        if jockey_weight == -1:
            return self.PLACEHOLDER_VALUE

        return jockey_weight

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


class WeightAllowance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.allowance == -1:
            return self.PLACEHOLDER_VALUE
        return horse.jockey.allowance
