from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class CurrentOddsExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Odds_Feature"

    def get_value(self, horse: Horse) -> float:
        race_card = horse.get_race(0)
        return race_card.get_current_odds_of_horse(horse.horse_id)
