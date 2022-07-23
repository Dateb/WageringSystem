from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class WeightAllowanceExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Weight_Allowance"

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.jockey.allowance
