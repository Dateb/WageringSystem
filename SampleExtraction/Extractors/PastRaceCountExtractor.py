from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PastRaceCountExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Past_Race_Count"

    def get_value(self, horse: Horse) -> int:
        base_race_card = horse.get_race(0)
        return len(base_race_card.form_table_of_horse(horse.horse_id))
