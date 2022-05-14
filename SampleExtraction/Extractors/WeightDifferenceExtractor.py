from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class WeightDifferenceExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = 0.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Weight_Difference"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        current_jockey = horse.raw_data["jockey"]
        if "weight" in current_jockey:
            current_weight = current_jockey["weight"]["weight"]

            previous_jockey = horse.get_race(1).get_data_of_subject(horse.subject_id)["jockey"]
            if "weight" in previous_jockey:
                previous_weight = previous_jockey["weight"]["weight"]
                return current_weight - previous_weight

        return self.PLACEHOLDER_VALUE
