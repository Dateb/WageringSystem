from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class RatingExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Rating"

    def get_value(self, horse_id: str, horse_data: dict) -> float:
        rating = horse_data[horse_id]['rating']
        if rating == '':
            return 0
        return rating
