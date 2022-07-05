from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class WinRateJockeyExtractor(FeatureExtractor):

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Win_Rate_Jockey_{self.__race_card_idx}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        win_rate = horse.jockey.win_rate
        if win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return 1 / (win_rate + 0.001)
