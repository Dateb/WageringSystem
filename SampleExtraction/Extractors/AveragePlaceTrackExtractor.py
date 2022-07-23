from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AveragePlaceTrackExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Average_Place_Track"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)

        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        n_past_races_of_same_track = 0

        total_place = 0
        for past_race in form_table:
            if past_race["trackName"] == base_race_card.title:
                if "finalPosition" in past_race:
                    n_past_races_of_same_track += 1
                    total_place += past_race["finalPosition"]

        if n_past_races_of_same_track == 0:
            return self.PLACEHOLDER_VALUE

        return total_place / n_past_races_of_same_track
