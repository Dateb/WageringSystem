from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class CurrentJockeyWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.weight == -1:
            return self.PLACEHOLDER_VALUE
        return float(horse.jockey.weight)


class WeightAllowance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.allowance == -1:
            return self.PLACEHOLDER_VALUE
        return horse.jockey.allowance


class OutOfHandicapWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.weight == -1:
            return self.PLACEHOLDER_VALUE

        return horse.jockey.weight - horse.handicap_weight
