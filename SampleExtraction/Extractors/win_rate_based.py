from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import win_rate_source


class HorseWinRate(FeatureExtractor):
    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Horse_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["subject_id"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["subject_id"])
        return get_win_rate_of_name(horse.name)


class JockeyWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Jockey_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["jockey_name"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["jockey_name"])
        return get_win_rate_of_name(horse.jockey_name)


class TrainerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Trainer_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["trainer_name"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["trainer_name"])
        return get_win_rate_of_name(horse.trainer_name)


class HorseJockeyWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Horse_Jockey_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["name", "jockey_name"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["name", "jockey_name"] )
        return get_win_rate_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attribute_groups.append(["name", "trainer_name"])

    def get_name(self) -> str:
        return "Horse_Trainer_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["name", "trainer_name"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["name", "trainer_name"])
        return get_win_rate_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = win_rate_source
        self.source.win_rate_attribute_groups.append(["name", "breeder"])

    def get_name(self) -> str:
        return "Horse_Breeder_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["name", "breeder"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["name", "breeder"])
        return get_win_rate_of_name(f"{horse.name}_{horse.breeder}")


class BreederWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Breeder_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["breeder"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["breeder"])
        return get_win_rate_of_name(horse.breeder)


class OwnerWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Owner_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["owner"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["owner"])
        return get_win_rate_of_name(horse.owner)


class SireWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Sire_Win_Rate"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if ["sire"] not in win_rate_source.win_rate_attribute_groups:
            win_rate_source.win_rate_attribute_groups.append(["sire"])
        return get_win_rate_of_name(horse.sire)


def get_win_rate_of_name(name: str) -> float:
    win_rate = win_rate_source.get_win_rate_of_name(name)
    if win_rate == -1:
        return float('NaN')
    return win_rate
