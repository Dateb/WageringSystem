import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse

HOUR_MAX = 24
MINUTE_MAX = 60
MONTH_MAX = 12
WEEKDAY_MAX = 7


class HourCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Hour_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.hour / HOUR_MAX)


class HourSinExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Hour_Sin"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.hour / HOUR_MAX)


class MinuteCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Minute_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.minute / MINUTE_MAX)


class MinuteSinExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Minute_Sin"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.minute / MINUTE_MAX)


class MonthCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Month_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * (race_card.datetime.month - 1) / MONTH_MAX)


class MonthSinExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Month_Sin"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * (race_card.datetime.month - 1) / MONTH_MAX)


class WeekDayCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Week_Day_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.cos(2 * np.pi * race_card.datetime.weekday() / WEEKDAY_MAX)


class WeekDaySinExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Week_Day_Sin"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return np.sin(2 * np.pi * race_card.datetime.weekday() / WEEKDAY_MAX)


class AbsoluteTime(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Absolute_Time"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.date_raw
