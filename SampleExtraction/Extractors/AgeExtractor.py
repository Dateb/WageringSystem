from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class AgeExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Age"

    def get_value(self, horse_id: str, horse_data: dict) -> int:
        return horse_data[horse_id]['age']
