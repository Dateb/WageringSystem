from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class JockeyWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        jockey_weight = horse.jockey.weight
        if jockey_weight == -1:
            return self.PLACEHOLDER_VALUE

        return jockey_weight


class WeightAllowance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.jockey.allowance
