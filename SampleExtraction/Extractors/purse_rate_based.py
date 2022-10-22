from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import purse_rate_source


class HorsePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.name)


class JockeyPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.jockey_name)


class TrainerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.trainer_name)


class HorseJockeyPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.name}_{horse.breeder}")


class BreederPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.breeder)


class OwnerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.owner)


class SirePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.sire)


class DamPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["dam"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.dam)


class DamSirePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["dam_sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(horse.dam_sire)


class JockeyDistancePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.distance}")


class JockeySurfacePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.surface}")


class JockeyTrackPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.track_name}")


class JockeyClassPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.jockey_name}_{race_card.race_class}")


class TrainerDistancePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.distance}")


class TrainerSurfacePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.surface}")


class TrainerTrackPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.track_name}")


class TrainerClassPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_show_rate_of_name(f"{horse.trainer_name}_{race_card.race_class}")


def get_show_rate_of_name(name: str) -> float:
    show_rate = purse_rate_source.get_average_of_name(name)
    if show_rate == -1:
        return float('NaN')
    return show_rate
