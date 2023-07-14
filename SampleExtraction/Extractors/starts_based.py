from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.time_calculation import get_day_difference


class LifeTimeStartCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return len(horse.form_table.past_forms) + 1


class OneYearStartCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 365
        ]
        return len(past_forms_this_year) + 1


class TwoYearStartCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_and_last_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 2 * 365
        ]
        return len(past_forms_this_and_last_year) + 1


class HasFewStartsInTwoYears(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms_this_and_last_year = [
            i for i in range(len(horse.form_table.past_forms)) if get_day_difference(race_card, horse, -1, i) <= 2 * 365
        ]
        return len(past_forms_this_and_last_year) < 13
