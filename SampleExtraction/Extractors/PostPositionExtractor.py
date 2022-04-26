from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class PostPositionExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Post_Position"

    def get_value(self, horse_id: str, horse_data: dict) -> str:
        if "postPosition" in horse_data[horse_id]:
            return horse_data[horse_id]["postPosition"]
        return "0"
