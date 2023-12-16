from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.average_based import ShowRateSource
from SampleExtraction.feature_sources.init import show_rate_source, FEATURE_SOURCES, dam_and_sire_average_momentum_source


class HorseShowRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.show_rate_source = ShowRateSource(window_size)
        self.show_rate_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.show_rate_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if self.show_rate_source.get_count_of_name(str(horse.subject_id)) < 3:
            return self.PLACEHOLDER_VALUE

        show_rate = self.show_rate_source.get_average_of_name(str(horse.subject_id))
        if show_rate == -1:
            return self.PLACEHOLDER_VALUE
        return show_rate

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


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


class DamSireShowRate(FeatureExtractor):

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
        return -1
    return show_rate
