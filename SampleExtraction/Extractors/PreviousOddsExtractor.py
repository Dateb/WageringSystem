from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PreviousOddsExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Odds"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_form = horse.form_table.past_forms[0]
        return previous_form.odds
