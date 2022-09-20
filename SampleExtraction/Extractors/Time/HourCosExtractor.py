import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class HourCosExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Hour_Cos"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        hour = race_card.datetime.hour
        hour_max = 23
        return np.cos(2 * np.pi * hour / hour_max)
