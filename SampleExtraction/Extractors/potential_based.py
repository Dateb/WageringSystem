from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class MaxPastRatingExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        past_ratings = [past_form.rating for past_form in horse.form_table.past_forms if past_form.rating != -1]

        if not past_ratings:
            return self.PLACEHOLDER_VALUE

        return max(past_ratings)
