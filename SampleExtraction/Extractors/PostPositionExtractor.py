from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PostPositionExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Post_Position"

    def get_value(self, horse: Horse) -> str:
        if "postPosition" in horse.raw_data:
            return horse.raw_data["postPosition"]
        return self.PLACEHOLDER_VALUE
