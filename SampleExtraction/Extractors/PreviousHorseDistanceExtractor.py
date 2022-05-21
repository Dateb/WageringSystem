from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PreviousHorseDistanceExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = -1.0

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Horse_Distance"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)
        horse_distances = base_race_card.horse_distances_of_horse(horse.horse_id)

        if horse_distances:
            return horse_distances[0]

        return self.PLACEHOLDER_VALUE
