from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class LayoffExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Layoff"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        if len(form_table.past_forms) == 0:
            return self.PLACEHOLDER_VALUE

        current_date = race_card.date
        previous_date = horse.form_table.past_forms[0].date

        return (current_date - previous_date).days
