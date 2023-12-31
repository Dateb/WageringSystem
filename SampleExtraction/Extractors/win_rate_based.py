from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.average_based import AverageWinProbabilitySource, WinRateSource, \
    AveragePlacePercentileSource, AverageMomentumSource, AverageVelocitySource


class WindowTimeLength(FeatureExtractor):

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        window_time_length = window_time_length_source.get_day_count_of_window(horse, self.window_size)

        if window_time_length is None:
            return self.PLACEHOLDER_VALUE

        return window_time_length

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


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


class BreederMomentum(FeatureExtractor):

    average_momentum_source.average_attribute_groups.append(["breeder"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if average_momentum_source.get_count_of_name(horse.breeder) < 20:
            return self.PLACEHOLDER_VALUE

        breeder_momentum = average_momentum_source.get_average_of_name(horse.breeder)

        if breeder_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return breeder_momentum


class OwnerMomentum(FeatureExtractor):

    average_momentum_source.average_attribute_groups.append(["owner"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if average_momentum_source.get_count_of_name(horse.owner) < 20:
            return self.PLACEHOLDER_VALUE

        owner_momentum = average_momentum_source.get_average_of_name(horse.owner)

        if owner_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return owner_momentum


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
