from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Sources import SireSource


class SireWinRateExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = SireSource.get_feature_source()

    def get_name(self) -> str:
        return "Sire_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_win_rate = self.source.get_sire_win_rate(horse)
        if sire_win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return self.source.get_sire_win_rate(horse)
