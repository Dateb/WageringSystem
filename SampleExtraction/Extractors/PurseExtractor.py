from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class PurseExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Purse"

    def get_value(self, horse_id: str, horse_data: dict) -> int:
        return horse_data[horse_id]['pp']['purse']
