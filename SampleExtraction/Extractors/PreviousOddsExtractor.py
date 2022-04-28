from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PreviousOddsExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Odds"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return 0.0

        previous_race = horse.get_race(1)
        horse_data = previous_race.get_data_of_subject(horse.subject_id)
        return horse_data["odds"]["PRC"]
