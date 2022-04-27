from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class NumPlaceJockeyExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Num_Place_Jockey"

    def get_value(self, horse: Horse) -> str:
        jockey = horse.raw_data["jockey"]
        jockey_stats = jockey["stats"]
        if jockey_stats is not False:
            return jockey_stats["numPlace"]

        return "0"
