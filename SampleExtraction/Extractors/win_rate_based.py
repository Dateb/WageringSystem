from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import win_rate_source


class HorseWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.name)


class JockeyWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.jockey_name)


class TrainerWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.trainer_name)


class HorseJockeyWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["name", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerWinRate(FeatureExtractor):
    win_rate_source.average_attribute_groups.append(["name", "trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["name", "breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.name}_{horse.breeder}")


class BreederWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.breeder)


class OwnerWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.owner)


class SireWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.sire)


class DamWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["dam"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.dam)


class DamSireWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["dam_sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(horse.dam_sire)


class JockeyDistanceWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["jockey_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.jockey_name}_{race_card.distance}")


class JockeySurfaceWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["jockey_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.jockey_name}_{race_card.surface}")


class JockeyTrackWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["jockey_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.jockey_name}_{race_card.track_name}")


class JockeyClassWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["jockey_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.jockey_name}_{race_card.race_class}")


class TrainerDistanceWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["trainer_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.trainer_name}_{race_card.distance}")


class TrainerSurfaceWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["trainer_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.trainer_name}_{race_card.surface}")


class TrainerTrackWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["trainer_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.trainer_name}_{race_card.track_name}")


class TrainerClassWinRate(FeatureExtractor):

    win_rate_source.average_attribute_groups.append(["trainer_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_win_rate_of_name(f"{horse.trainer_name}_{race_card.race_class}")


def get_win_rate_of_name(name: str) -> float:
    win_rate = win_rate_source.get_average_of_name(name)
    if win_rate == -1:
        return float('NaN')
    return win_rate
