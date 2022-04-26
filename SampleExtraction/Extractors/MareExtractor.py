from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class MareExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Mare"

    def get_value(self, horse_id: str, horse_data: dict) -> int:
        gelding_indicator = horse_data[horse_id]["gender"] == "M"

        return int(gelding_indicator)
