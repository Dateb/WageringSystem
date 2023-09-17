from statistics import mean

import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import speed_figures_source


class CurrentSpeedFigure(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        speed_figure = speed_figures_source.get_current_speed_figure(horse.name)
        if speed_figure == -1:
            return self.PLACEHOLDER_VALUE
        return speed_figure + 10


class MeanSpeedDiff(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        speed_figures_buffer = speed_figures_source.get_current_speed_figure(horse.subject_id)
        if speed_figures_buffer == -1 or len(speed_figures_buffer) == 1:
            return self.PLACEHOLDER_VALUE

        speed_figure_differences = np.diff(speed_figures_buffer)

        return mean(speed_figure_differences)


class BestLifeTimeSpeedFigure(FeatureExtractor):
    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return speed_figures_source.get_max_speed_figure(horse.subject_id)
