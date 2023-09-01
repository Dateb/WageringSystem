from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor

class TrainerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.win_rate == -1:
            return -1
        return horse.trainer.win_rate


class TrainerPlaceRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.place_rate == -1:
            return -1
        return horse.trainer.place_rate


class TrainerEarningsRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if horse.trainer.earnings_rate == -1:
            return -1
        return horse.trainer.earnings_rate
