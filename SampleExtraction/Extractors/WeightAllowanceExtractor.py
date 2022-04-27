from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class WeightAllowanceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Weight_Allowance"

    def get_value(self, horse: Horse) -> str:
        jockey = horse.raw_data["jockey"]
        if "weight" in jockey:
            return jockey["weight"]["allowance"]

        return "0"
