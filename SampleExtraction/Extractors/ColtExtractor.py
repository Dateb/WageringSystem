from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class ColtExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Colt"

    def get_value(self, horse_id: str, horse_data: dict) -> int:
        gelding_indicator = horse_data[horse_id]["gender"] == "C"

        return int(gelding_indicator)
