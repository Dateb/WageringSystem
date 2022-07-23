from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class MaxPastRatingExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Max_Past_Rating"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)
        ratings = base_race_card.past_ratings_of_horse(horse.horse_id)

        if not ratings:
            return self.PLACEHOLDER_VALUE

        return max(ratings)
