from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class BlinkerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Has_Blinker"

    def get_value(self, horse: Horse) -> int:
        blinker_indicator = horse.raw_data["blinkers"]

        return int(blinker_indicator)
