from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PreviousClassExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Class"

    def get_value(self, horse: Horse) -> int:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        previous_race = horse.get_race(1)
        previous_class = previous_race.race_class

        try:
            previous_class = int(previous_class)
        except ValueError:
            previous_class = self.PLACEHOLDER_VALUE

        return previous_class
