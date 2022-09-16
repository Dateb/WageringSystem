from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Sources import NamedWinRateSource


class OwnerWinRateExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = NamedWinRateSource.get_feature_source()

    def get_name(self) -> str:
        return "Owner_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        owner_win_rate = self.source.get_win_rate_of_name(horse.owner)
        if owner_win_rate == -1:
            return self.PLACEHOLDER_VALUE
        print(owner_win_rate)
        return owner_win_rate
