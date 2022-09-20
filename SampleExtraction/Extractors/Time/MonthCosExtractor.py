import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class MonthCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Month_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        month = race_card.datetime.month - 1
        month_max = 11
        return np.cos(2 * np.pi * month / month_max)
