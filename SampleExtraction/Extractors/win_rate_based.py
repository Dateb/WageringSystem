from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.average_based import WinProbabilitySource, WinRateSource, \
    AveragePlacePercentileSource, AverageMomentumSource
from SampleExtraction.feature_sources.init import win_rate_source, FEATURE_SOURCES, \
    window_time_length_source


class HorseWinProbability(FeatureExtractor):

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.win_probability_source = WinProbabilitySource(window_size)
        self.win_probability_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.win_probability_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        win_probability = self.win_probability_source.get_average_of_name(str(horse.subject_id))
        if win_probability == -1:
            return self.PLACEHOLDER_VALUE
        return win_probability

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


class HorseWinRate(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.win_rate_source = WinRateSource(window_size)
        self.win_rate_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.win_rate_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        win_rate = self.win_rate_source.get_average_of_name(str(horse.subject_id))

        if win_rate == -1:
            return self.PLACEHOLDER_VALUE

        return win_rate

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


class HorsePlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.place_percentile_source = AveragePlacePercentileSource(window_size)
        self.place_percentile_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.place_percentile_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_place_percentile = self.place_percentile_source.get_average_of_name(str(horse.subject_id))
        if average_place_percentile == -1:
            return self.PLACEHOLDER_VALUE
        return average_place_percentile

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


class HorseMomentum(FeatureExtractor):

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.momentum_source = AverageMomentumSource(window_size)
        self.momentum_source.average_attribute_groups.append(["subject_id"])
        FEATURE_SOURCES.append(self.momentum_source)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_momentum = self.momentum_source.get_average_of_name(str(horse.subject_id))

        if average_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return average_momentum

    def get_name(self) -> str:
        return f"{type(self).__name__}_{self.window_size}"


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
