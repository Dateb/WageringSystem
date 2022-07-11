from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class BlinkerExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Has_Blinker"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.has_blinkers)
