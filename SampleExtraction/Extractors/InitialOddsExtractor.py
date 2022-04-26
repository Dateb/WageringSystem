from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class InitialOddsExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Initial_Odds"

    def get_value(self, horse_id: str, horse_data: dict) -> float:
        if "fixedOddsHistory" in horse_data[horse_id]:
            return horse_data[horse_id]["fixedOddsHistory"][-1]
        return 0
