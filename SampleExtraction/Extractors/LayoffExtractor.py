from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class LayoffExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = -1.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Layoff"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        current_race = horse.get_race(0)
        previous_race = horse.get_race(1)

        time_since_last_race = current_race.start_time - previous_race.start_time
        return 1 / time_since_last_race
