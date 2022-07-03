from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AgeExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Age"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return horse.age
