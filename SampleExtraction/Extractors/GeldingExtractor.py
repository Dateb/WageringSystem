from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class GeldingExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Gelding"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        gelding_indicator = horse.gender == "G"

        return int(gelding_indicator)
