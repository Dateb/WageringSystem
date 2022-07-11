import statistics

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AveragePlaceLifetimeExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Average_Place_Lifetime"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_forms = horse.form_table.past_forms

        if not past_forms:
            return self.PLACEHOLDER_VALUE

        past_places = [past_form.final_position for past_form in past_forms]
        valid_past_places = [past_place for past_place in past_places if past_place != -1]

        if not valid_past_places:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(valid_past_places)
