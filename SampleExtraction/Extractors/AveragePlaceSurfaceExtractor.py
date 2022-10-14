import statistics

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AveragePlaceSurfaceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_forms = horse.form_table.past_forms
        if not past_forms:
            return self.PLACEHOLDER_VALUE

        past_forms_same_surface = [
            past_form for past_form in past_forms if past_form.surface == race_card.surface
        ]

        if not past_forms_same_surface:
            return self.PLACEHOLDER_VALUE

        places = [
            past_form.final_position for past_form in past_forms_same_surface if past_form.final_position > 0
        ]

        if not places:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(places)
