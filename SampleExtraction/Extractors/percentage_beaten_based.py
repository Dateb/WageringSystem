from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import percentage_beaten_source, horse_name_to_subject_id_source


class HorsePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.name)


class JockeyPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.jockey_name)


class TrainerPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.trainer_name)


class HorseJockeyPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["name", "jockey_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.name}_{horse.jockey_name}")


class HorseTrainerPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["name", "trainer_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.name}_{horse.trainer_name}")


class HorseBreederPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["name", "breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.name}_{horse.breeder}")


class BreederPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.breeder)


class OwnerPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.owner)


class SirePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_percentage_beaten = get_percentage_beaten_of_name(horse.sire)

        if sire_percentage_beaten == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_percentage_beaten


class DamPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["dam"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_percentage_beaten = get_percentage_beaten_of_name(horse.dam)

        if dam_percentage_beaten == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_percentage_beaten


class DamSirePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["dam_sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(horse.dam_sire)


class JockeyDistancePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["jockey_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.jockey_name}_{race_card.distance}")


class JockeySurfacePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["jockey_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.jockey_name}_{race_card.surface}")


class JockeyTrackPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["jockey_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.jockey_name}_{race_card.track_name}")


class JockeyClassPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["jockey_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.jockey_name}_{race_card.race_class}")


class TrainerDistancePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["trainer_name", "distance"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.trainer_name}_{race_card.distance}")


class TrainerSurfacePercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["trainer_name", "surface"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.trainer_name}_{race_card.surface}")


class TrainerTrackPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["trainer_name", "track_name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.trainer_name}_{race_card.track_name}")


class TrainerClassPercentageBeaten(FeatureExtractor):

    percentage_beaten_source.average_attribute_groups.append(["trainer_name", "race_class"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_percentage_beaten_of_name(f"{horse.trainer_name}_{race_card.race_class}")


def get_percentage_beaten_of_name(name: str) -> float:
    show_rate = percentage_beaten_source.get_average_of_name(name)
    return show_rate
