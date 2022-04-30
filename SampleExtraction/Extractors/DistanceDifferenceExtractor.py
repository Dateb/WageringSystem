from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class DistanceDifferenceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Distance_Difference"

    def get_value(self, horse: Horse) -> int:
        if not horse.has_past_races:
            return -1

        previous_race = horse.get_race(1)
        current_race = horse.get_race(0)
        return current_race.distance - previous_race.distance
