from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class ColtExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Colt"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        gelding_indicator = horse.gender == "C"

        return int(gelding_indicator)
