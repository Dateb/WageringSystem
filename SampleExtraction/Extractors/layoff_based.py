from abc import ABC
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import previous_date_source
from SampleExtraction.time_calculation import get_day_difference


class Layoff(FeatureExtractor, ABC):

    PLACEHOLDER_VALUE = -1

    def __init__(self, attribute_group: List[str]):
        super().__init__()
        self.attribute_group = attribute_group
        previous_date_source.previous_value_attribute_groups.append(self.attribute_group)

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        attribute_group_key = previous_date_source.get_attribute_group_key(race_card, horse, self.attribute_group)
        previous_datetime = previous_date_source.get_previous_of_name(attribute_group_key)

        if previous_datetime is None:
            return self.PLACEHOLDER_VALUE

        layoff = (race_card.datetime - previous_datetime).days
        return layoff / 1000


class PreviousRaceLayoff(Layoff):

    def __init__(self):
        super().__init__(["subject_id"])


class SameTrackLayoff(Layoff):

    def __init__(self):
        super().__init__(["subject_id", "track_name"])


class SameClassLayoff(Layoff):

    def __init__(self):
        super().__init__(["subject_id", "race_class"])


class SameSurfaceLayoff(Layoff):

    def __init__(self):
        super().__init__(["subject_id", "surface"])


class HasOptimalBreak(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE
        return 30 <= get_day_difference(race_card, horse, -1, 0) <= 60


class ComingFromLayoff(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if len(horse.form_table.past_forms) < 2:
            return self.PLACEHOLDER_VALUE

        today_previous_day_difference = get_day_difference(race_card, horse, -1, 0)
        previous_to_penultimate_day_difference = get_day_difference(race_card, horse, 0, 1)

        had_layoff = previous_to_penultimate_day_difference >= 90
        lost_layoff = today_previous_day_difference < 90
        return int(had_layoff and lost_layoff)


class HasWonAfterLongBreak(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        n_past_forms = len(horse.form_table.past_forms)

        if n_past_forms < 2:
            return False

        for i in range(n_past_forms - 1):
            past_form = horse.form_table.past_forms[i]
            if past_form.has_won and get_day_difference(race_card, horse, i, i+1) > 90:
                return True

        return False
