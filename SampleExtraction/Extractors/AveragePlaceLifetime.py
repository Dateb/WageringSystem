from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class AveragePlaceLifetimeExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Average_Place_Lifetime"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)

        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        n_past_races = 0

        total_place = 0
        for past_race in form_table:
            if "finalPosition" in past_race:
                n_past_races += 1
                total_place += past_race["finalPosition"]

        if n_past_races == 0:
            return self.PLACEHOLDER_VALUE

        return total_place / n_past_races
