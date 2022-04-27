from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class WeightJockeyExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Weight_Jockey"

    def get_value(self, horse: Horse) -> str:
        jockey = horse.raw_data["jockey"]
        if "weight" in jockey:
            return jockey["weight"]["weight"]

        return "0"
