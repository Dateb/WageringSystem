import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class WeekDayCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Week_Day_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        weekday = race_card.datetime.weekday()
        weekday_max = 7
        return np.cos(2 * np.pi * weekday / weekday_max)
