from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import show_rate_source


class HorseShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.name)


class JockeyShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.jockey_name)


class TrainerShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.trainer_name)


class HorseJockeyShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["name", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["name", "trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["name", "breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.breeder}")


class BreederShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.breeder)


class OwnerShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.owner)


class SireShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.sire)


class DamShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["dam"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.dam)


class DamSireShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["dam_sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.dam_sire)


class JockeyDistanceShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["jockey_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.distance}")


class JockeySurfaceShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["jockey_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.surface}")


class JockeyTrackShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["jockey_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.track_name}")


class JockeyClassShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["jockey_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.race_class}")


class TrainerDistanceShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["trainer_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.distance}")


class TrainerSurfaceShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["trainer_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.surface}")


class TrainerTrackShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["trainer_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.track_name}")


class TrainerClassShowRate(FeatureExtractor):

    show_rate_source.average_attribute_groups.append(["trainer_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.race_class}")


def get_show_rate_of_name(name: str) -> float:
    show_rate = show_rate_source.get_average_of_name(name)
    if show_rate == -1:
        return float('NaN')
    return show_rate
