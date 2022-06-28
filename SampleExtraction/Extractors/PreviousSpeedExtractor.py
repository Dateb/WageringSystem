from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PreviousSpeedExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Speed"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)
        horse_speeds = base_race_card.past_speeds_of_horse(horse.horse_id)

        if horse_speeds[0] == -1:
            return self.PLACEHOLDER_VALUE

        return horse_speeds[0]
