from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import purse_rate_source, horse_name_to_subject_id_source


class HorsePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        purse_rate = purse_rate_source.get_average_of_name(str(horse.subject_id))

        if purse_rate == -1:
            return -1
        return purse_rate


class JockeyPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(horse.jockey_name)


class TrainerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(horse.trainer_name)


class HorseJockeyPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["name", "breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.name}_{horse.breeder}")


class BreederPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(horse.breeder)


class OwnerPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(horse.owner)


class SirePurseRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_purse_rate = get_purse_rate_of_name(horse.sire)

        if sire_purse_rate == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_purse_rate / 10000


class DamPurseRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_purse_rate = get_purse_rate_of_name(horse.dam)

        if dam_purse_rate == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_purse_rate / 10000


class DamSirePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["dam_sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(horse.dam_sire)


class JockeyDistancePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.jockey_name}_{race_card.distance}")


class JockeySurfacePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.jockey_name}_{race_card.surface}")


class JockeyTrackPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.jockey_name}_{race_card.track_name}")


class JockeyClassPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["jockey_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.jockey_name}_{race_card.race_class}")


class TrainerDistancePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.trainer_name}_{race_card.distance}")


class TrainerSurfacePurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.trainer_name}_{race_card.surface}")


class TrainerTrackPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.trainer_name}_{race_card.track_name}")


class TrainerClassPurseRate(FeatureExtractor):

    purse_rate_source.average_attribute_groups.append(["trainer_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_purse_rate_of_name(f"{horse.trainer_name}_{race_card.race_class}")


def get_purse_rate_of_name(name: str) -> float:
    purse_rate = purse_rate_source.get_average_of_name(name)
    if purse_rate == -1:
        return -1
    return purse_rate
