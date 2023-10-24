from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import win_rate_source, speed_figures_source, \
    horse_name_to_subject_id_source


class HorseWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0
    win_rate_source.average_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        win_rate = get_win_rate_of_name(horse.name)
        if win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return win_rate


# class JockeyWinRate(FeatureExtractor):
#
#     win_rate_source.average_attribute_groups.append(["jockey_name"])
#
#     def __init__(self):
#         super().__init__()
#
#     def get_value(self, race_card: RaceCard, horse: Horse) -> float:
#         win_rate = get_win_rate_of_name(horse.jockey_name)
#         if win_rate == -1:
#             return -1
#         return win_rate + 1


# class TrainerWinRate(FeatureExtractor):
#
#     win_rate_source.average_attribute_groups.append(["trainer_name"])
#
#     def __init__(self):
#         super().__init__()
#
#     def get_value(self, race_card: RaceCard, horse: Horse) -> float:
#         win_rate = get_win_rate_of_name(horse.trainer_name)
#         if win_rate == -1:
#             return -1
#         return win_rate + 1


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

    PLACEHOLDER_VALUE = -1
    win_rate_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        breeder_win_rate = get_win_rate_of_name(horse.breeder)
        if breeder_win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return breeder_win_rate


class OwnerWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = -1
    win_rate_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        owner_win_rate = get_win_rate_of_name(horse.owner)
        if owner_win_rate == -1:
            return self.PLACEHOLDER_VALUE
        return owner_win_rate


class SireWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = -1
    win_rate_source.average_attribute_groups.append(["sire"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_win_rate = get_win_rate_of_name(horse.sire)

        if sire_win_rate == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_win_rate


class DamWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = -1
    win_rate_source.average_attribute_groups.append(["dam"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_win_rate = get_win_rate_of_name(horse.dam)
        if dam_win_rate == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            print('yellow')
            return self.PLACEHOLDER_VALUE

        return dam_win_rate


class DamSireWinRate(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return speed_figures_source.get_current_speed_figure(horse.dam_sire)


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
        win_rate = get_win_rate_of_name(f"{horse.jockey_name}_{race_card.surface}")
        if win_rate == -1:
            return -1

        return win_rate + 1


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

    return win_rate
