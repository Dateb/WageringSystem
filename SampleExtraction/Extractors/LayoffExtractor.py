from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class LayoffExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Layoff"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        current_race = horse.get_race(0)
        previous_race = horse.get_race(1)

        return current_race.start_time - previous_race.start_time
