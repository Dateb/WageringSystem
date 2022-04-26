from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class WeightJockeyExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Weight_Jockey"

    def get_value(self, horse_id: str, horse_data: dict) -> str:
        jockey = horse_data[horse_id]["jockey"]
        if "weight" in jockey:
            return jockey["weight"]["weight"]

        return "0"
