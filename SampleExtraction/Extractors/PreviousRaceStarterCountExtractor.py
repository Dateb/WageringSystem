from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PreviousRaceStarterCountExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Race_Starter_Count"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return 0.0

        previous_race = horse.get_race(1)
        return previous_race.n_runners
