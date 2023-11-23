from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import life_time_start_count_source
from SampleExtraction.time_calculation import get_day_difference


class LifeTimeStartCount(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        start_count = life_time_start_count_source.get_previous_of_name(str(horse.subject_id))

        if start_count is None:
            return self.PLACEHOLDER_VALUE
        return start_count / 100


class LifeTimeWinCount(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        win_count = life_time_win_count_source.get_previous_of_name(str(horse.subject_id))

        if win_count is None:
            return self.PLACEHOLDER_VALUE
        return win_count / 20


class LifeTimePlaceCount(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        place_count = life_time_place_count_source.get_previous_of_name(str(horse.subject_id))

        if place_count is None:
            return self.PLACEHOLDER_VALUE
        return place_count / 20


class OneYearStartCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 365
        ]
        return len(past_forms_this_year)


class TwoYearStartCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_and_last_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 2 * 365
        ]
        return len(past_forms_this_and_last_year)


class HasFewStartsInTwoYears(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_and_last_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 2 * 365
        ]
        return len(past_forms_this_and_last_year) < 13
