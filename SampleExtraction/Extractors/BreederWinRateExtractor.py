from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Sources import NamedWinRateSource


class BreederWinRateExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = NamedWinRateSource.get_feature_source()

    def get_name(self) -> str:
        return "Breeder_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        breeder_win_rate = self.source.get_win_rate_of_name(horse.breeder)
        if breeder_win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return breeder_win_rate
