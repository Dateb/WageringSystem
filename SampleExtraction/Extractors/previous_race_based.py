from abc import ABC
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import previous_win_prob_source, previous_place_percentile_source, \
    previous_relative_distance_behind_source, PreviousValueSource


class PreviousWinProbability(FeatureExtractor):

    previous_win_prob_source.previous_value_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_win_prob = previous_win_prob_source.get_previous_of_name(str(horse.subject_id))

        if previous_win_prob is None:
            return self.PLACEHOLDER_VALUE

        return previous_win_prob


class PreviousSameAttributeWinProbDifference(FeatureExtractor, ABC):

    PLACEHOLDER_VALUE = 0

    def __init__(self, previous_value_source: PreviousValueSource, attribute_group: List[str]):
        super().__init__()
        self.previous_value_source = previous_value_source
        self.attribute_group = attribute_group
        self.previous_value_source.previous_value_attribute_groups.append(attribute_group)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_win_prob_key = self.previous_value_source.get_attribute_group_key(race_card, horse, self.attribute_group)

        previous_same_attribute_win_prob = self.previous_value_source.get_previous_of_name(previous_win_prob_key)
        previous_win_prob = self.previous_value_source.get_previous_of_name(str(horse.subject_id))

        if previous_same_attribute_win_prob is None:
            return self.PLACEHOLDER_VALUE

        return previous_same_attribute_win_prob - previous_win_prob


class PreviousSameSurfaceWinProbability(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_win_prob_source, ["subject_id", "surface"])


class PreviousSameTrackWinProbability(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_win_prob_source, ["subject_id", "track_name"])


class PreviousSameRaceClassWinProbability(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_win_prob_source, ["subject_id", "race_class"])


class PreviousSameSurfacePlacePercentile(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_place_percentile_source, ["subject_id", "surface"])


class PreviousSameTrackPlacePercentile(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_place_percentile_source, ["subject_id", "track_name"])


class PreviousSameRaceClassPlacePercentile(PreviousSameAttributeWinProbDifference):

    def __init__(self):
        super().__init__(previous_place_percentile_source, ["subject_id", "race_class"])


class PreviousPlacePercentile(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_place_percentile = previous_place_percentile_source.get_previous_of_name(str(horse.subject_id))

        if previous_place_percentile is None:
            return self.PLACEHOLDER_VALUE

        return previous_place_percentile


class PreviousRelativeDistanceBehind(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_relative_distance_behind = previous_relative_distance_behind_source.get_previous_of_name(str(horse.subject_id))

        if previous_relative_distance_behind is None:
            return self.PLACEHOLDER_VALUE

        return previous_relative_distance_behind


class PreviousFasterThanFraction(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE

        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_n_horses = horse.form_table.past_forms[0].n_horses

        if previous_n_horses == 1:
            return self.PLACEHOLDER_VALUE

        return abs(int(horse.previous_performance) - 1) / (previous_n_horses - 1) + 1


class PreviousSlowerThanFraction(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE

        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_n_horses = horse.form_table.past_forms[0].n_horses

        if previous_n_horses == 1:
            return self.PLACEHOLDER_VALUE

        return abs(previous_n_horses - int(horse.previous_performance)) / (previous_n_horses - 1) + 1


class PulledUpPreviousRace(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.previous_performance == "PU")
