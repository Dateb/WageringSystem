from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PurseExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Purse"

    def get_value(self, horse: Horse) -> int:
        return horse.raw_data['pp']['purse']
