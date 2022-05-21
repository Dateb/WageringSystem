from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class DistanceDifferenceExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = 0.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Distance_Difference"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        previous_race = horse.get_race(1)
        current_race = horse.get_race(0)
        return 1 / (current_race.distance - previous_race.distance + 0.001)
