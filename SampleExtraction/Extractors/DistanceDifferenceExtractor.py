from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class DistanceDifferenceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Distance_Difference"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_distance = race_card.distance
        form_table = horse.form_table
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_distance = form_table.past_forms[0].distance
        distance_difference = current_distance - previous_distance

        return 1 / (distance_difference + 0.001)
