from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import show_rate_source, average_win_probability_source, \
    average_place_percentile_source, average_momentum_source


class HorseJockeyWinProbability(FeatureExtractor):

    average_win_probability_source.average_attribute_groups.append(["subject_id", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = average_win_probability_source.get_attribute_group_key(race_card, horse, ["subject_id", "jockey_name"])
        horse_jockey_win_probability = average_win_probability_source.get_average_of_name(key)

        if horse_jockey_win_probability == -1:
            return self.PLACEHOLDER_VALUE

        return horse_jockey_win_probability


class HorseJockeyPlacePercentile(FeatureExtractor):

    average_place_percentile_source.average_attribute_groups.append(["subject_id", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = average_place_percentile_source.get_attribute_group_key(race_card, horse, ["subject_id", "jockey_name"])
        horse_jockey_place_percentile = average_place_percentile_source.get_average_of_name(key)

        if horse_jockey_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        return horse_jockey_place_percentile


class HorseJockeyMomentum(FeatureExtractor):

    average_momentum_source.average_attribute_groups.append(["subject_id", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = average_momentum_source.get_attribute_group_key(race_card, horse, ["subject_id", "jockey_name"])
        horse_jockey_momentum = average_momentum_source.get_average_of_name(key)

        if horse_jockey_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return horse_jockey_momentum


class HorseJockeyShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["subject_id", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = show_rate_source.get_attribute_group_key(race_card, horse, ["subject_id", "jockey_name"])
        horse_jockey_show_rate = show_rate_source.get_average_of_name(key)

        if horse_jockey_show_rate == -1:
            return self.PLACEHOLDER_VALUE

        return horse_jockey_show_rate
