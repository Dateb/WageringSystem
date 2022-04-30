from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class TrackGoingDifferenceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Track_Going_Difference"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return 0.0

        previous_race = horse.get_race(1)
        current_race = horse.get_race(0)
        return current_race.track_going - previous_race.track_going
