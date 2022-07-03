from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class WinRateLifetimeExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Win_Rate_Lifetime"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table

        n_past_forms = len(horse.form_table.past_forms)
        if n_past_forms == 0:
            return self.PLACEHOLDER_VALUE

        n_past_wins = sum([past_form.has_won for past_form in form_table.past_forms])

        return n_past_wins / n_past_forms
