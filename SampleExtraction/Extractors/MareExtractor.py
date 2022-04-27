from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class MareExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Mare"

    def get_value(self, horse: Horse) -> int:
        gelding_indicator = horse.raw_data["gender"] == "M"

        return int(gelding_indicator)
