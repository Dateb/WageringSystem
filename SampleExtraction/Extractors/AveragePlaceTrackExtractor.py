import statistics

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AveragePlaceTrackExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Average_Place_Track"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_forms = horse.form_table.past_forms
        if not past_forms:
            return self.PLACEHOLDER_VALUE

        past_forms_same_track = [
            past_form for past_form in past_forms if past_form.track_name == race_card.track_name
        ]

        if not past_forms_same_track:
            return self.PLACEHOLDER_VALUE

        places = [
            past_form.final_position for past_form in past_forms_same_track if past_form.final_position > 0
        ]

        if not places:
            return self.PLACEHOLDER_VALUE

        return statistics.mean(places)
