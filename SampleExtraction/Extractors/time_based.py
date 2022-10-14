import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse

HOUR_MAX = 24
MINUTE_MAX = 60
MONTH_MAX = 12
WEEKDAY_MAX = 7


class HourCos(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.hour / HOUR_MAX)


class HourSin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.hour / HOUR_MAX)


class MinuteCos(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.minute / MINUTE_MAX)


class MinuteSin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.minute / MINUTE_MAX)


class MonthCos(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * (race_card.datetime.month - 1) / MONTH_MAX)


class MonthSin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * (race_card.datetime.month - 1) / MONTH_MAX)


class WeekDayCos(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.weekday() / WEEKDAY_MAX)


class WeekDaySin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.weekday() / WEEKDAY_MAX)


class AbsoluteTime(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.date_raw
