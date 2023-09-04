from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor

class TrainerWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return horse.trainer.win_rate


class TrainerPlaceRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.place_rate == -1:
            return self.PLACEHOLDER_VALUE
        return horse.trainer.place_rate


class TrainerEarningsRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.earnings_rate == -1:
            return self.PLACEHOLDER_VALUE
        return horse.trainer.earnings_rate
