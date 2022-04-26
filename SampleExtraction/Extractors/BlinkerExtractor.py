from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class BlinkerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Has_Blinker"

    def get_value(self, horse_id: str, horse_data: dict) -> int:
        blinker_indicator = horse_data[horse_id]["blinkers"]

        return int(blinker_indicator)
