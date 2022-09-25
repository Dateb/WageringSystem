from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class IsGelding(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Gelding"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        is_gelding = horse.gender == "G"

        return int(is_gelding)


class IsMare(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Mare"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        is_mare = horse.gender == "M"

        return int(is_mare)


class IsColt(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Is_Colt"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        is_colt = horse.gender == "C"

        return int(is_colt)

