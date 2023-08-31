from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse

class JockeyWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.win_rate == -1:
            return -1
        return horse.jockey.win_rate + 1


class JockeyPlaceRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.place_rate == -1:
            return -1
        return horse.jockey.place_rate + 1


class JockeyEarningsRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.jockey.earnings_rate == -1:
            return -1
        return horse.jockey.earnings_rate + 1000


class JockeyWeight(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(horse.jockey.weight)


class WeightAllowance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.jockey.allowance
