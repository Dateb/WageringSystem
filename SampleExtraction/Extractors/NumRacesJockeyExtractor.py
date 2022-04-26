from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor


class NumRacesJockeyExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Num_Races_Jockey"

    def get_value(self, horse_id: str, horse_data: dict) -> str:
        jockey = horse_data[horse_id]["jockey"]
        jockey_stats = jockey["stats"]
        if jockey_stats is not False:
            return jockey_stats["numRaces"]

        return "0"
