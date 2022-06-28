from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class TrackPurseExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Track_Purse"

    def get_value(self, horse: Horse) -> int:
        base_race_card = horse.get_race(0)

        purse_history = base_race_card.purse_history_of_horse_by_track(horse.horse_id)

        if not purse_history:
            return self.PLACEHOLDER_VALUE

        return sum(purse_history)
