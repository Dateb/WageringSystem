import statistics

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PurseExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Purse"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_forms = horse.form_table.past_forms
        purses = [past_form.purse for past_form in past_forms]

        if not purses:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(purses)
