from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class JockeyWeightExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Jockey_Weight"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        jockey_weight = horse.jockey.weight
        if jockey_weight == -1:
            return self.PLACEHOLDER_VALUE

        return jockey_weight
