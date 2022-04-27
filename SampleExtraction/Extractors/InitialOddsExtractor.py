from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class InitialOddsExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Initial_Odds"

    def get_value(self, horse: Horse) -> float:
        if "fixedOddsHistory" in horse.raw_data:
            return horse.raw_data["fixedOddsHistory"][-1]
        return 0
