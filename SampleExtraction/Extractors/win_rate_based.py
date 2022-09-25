from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Sources.WinRateSource import win_rate_source, WinRateSource


class HorseWinRate(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("name")

    def get_name(self) -> str:
        return "Horse_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.name)


class JockeyWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("jockey_name")

    def get_name(self) -> str:
        return "Jockey_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.jockey_name)


class TrainerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("trainer_name")

    def get_name(self) -> str:
        return "Trainer_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.trainer_name)


class BreederWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("breeder")

    def get_name(self) -> str:
        return "Breeder_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.breeder)


class OwnerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("owner")

    def get_name(self) -> str:
        return "Owner_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.owner)


class SireWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attributes.append("sire")

    def get_name(self) -> str:
        return "Sire_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(self.source, horse.sire)


def get_win_rate_of_name(source: WinRateSource, name: str) -> float:
    win_rate = source.get_win_rate_of_name(name)
    if win_rate == -1:
        return float('NaN')
    return win_rate
