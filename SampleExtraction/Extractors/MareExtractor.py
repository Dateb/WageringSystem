from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class MareExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Mare"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        gelding_indicator = horse.gender == "M"

        return int(gelding_indicator)
