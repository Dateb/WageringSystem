from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PastMaxSpeedSameGoingExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Past_Max_Speed_Same_Going"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)
        horse_speeds = base_race_card.past_speeds_of_horse_same_going(horse.horse_id)

        if not horse_speeds:
            return self.PLACEHOLDER_VALUE

        return max(horse_speeds)
