from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import previous_win_prob_source, previous_place_percentile_source, \
    previous_relative_distance_behind_source


class PreviousWinProbability(FeatureExtractor):

    previous_win_prob_source.previous_value_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_win_prob = previous_win_prob_source.get_previous_of_name(horse.name)

        return previous_win_prob


class PreviousPlacePercentile(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_place_percentile = previous_place_percentile_source.get_previous_of_name(str(horse.subject_id))

        return previous_place_percentile


class PreviousRelativeDistanceBehind(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_relative_distance_behind = previous_relative_distance_behind_source.get_previous_of_name(str(horse.subject_id))

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
