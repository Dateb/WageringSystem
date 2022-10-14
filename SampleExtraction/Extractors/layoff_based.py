from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.time_calculation import get_day_difference


class HasOptimalBreak(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE
        return 30 <= get_day_difference(race_card, horse, -1, 0) <= 60


class HasLongBreak(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE
        return get_day_difference(race_card, horse, -1, 0) > 90


class HasVeryLongBreak(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE
        return get_day_difference(race_card, horse, -1, 0) > 180


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
