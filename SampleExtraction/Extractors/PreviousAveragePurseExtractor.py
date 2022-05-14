from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PreviousAveragePurseExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = 0.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Average_Purse"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        previous_race = horse.get_race(1)
        horses = previous_race.horses
        previous_purses = [horses[horse_id]["pp"]["purse"] for horse_id in horses]

        return sum(previous_purses) / len(previous_purses)
