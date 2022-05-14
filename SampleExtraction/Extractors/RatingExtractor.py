from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class RatingExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = 0.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Rating"

    def get_value(self, horse: Horse) -> float:
        rating = horse.raw_data['rating']
        if rating == '':
            return self.PLACEHOLDER_VALUE
        return rating
