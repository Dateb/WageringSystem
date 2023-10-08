import datetime

import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse

HOUR_MAX = 24
MINUTE_MAX = 60
MONTH_MAX = 12

DAY_OF_YEAR_MAX = 367
WEEKDAY_MAX = 7

MINUTES_INTO_DAY_MAX = 1440


class DayOfYearCos(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        day_of_year = race_card.date.timetuple().tm_yday
        return np.cos(2 * np.pi * day_of_year / DAY_OF_YEAR_MAX)


class DayOfYearSin(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        day_of_year = race_card.date.timetuple().tm_yday
        return np.sin(2 * np.pi * day_of_year / DAY_OF_YEAR_MAX)


class MinutesIntoDay(FeatureExtractor):
    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        race_card_date_time = race_card.datetime
        earliest_race_time = datetime.datetime(
            year=race_card_date_time.year,
            month=race_card_date_time.month,
            day=race_card_date_time.day,
            hour=12,
            minute=0,
            second=0,
        )
        minutes_into_day = (race_card_date_time - earliest_race_time).seconds / 60
        return minutes_into_day / MINUTES_INTO_DAY_MAX


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
