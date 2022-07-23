from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PastRaceCountExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Past_Race_Count"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return len(horse.form_table.past_forms)
