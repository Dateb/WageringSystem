from statistics import mean

import numpy as np

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import speed_figures_source


class CurrentSpeedFigure(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_speed_figure = speed_figures_source.get_current_speed_figure(horse.subject_id)
        if current_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return current_speed_figure


class BaseTime(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        base_time_category = race_card.get_base_time_estimate_of_horse(horse)

        return base_time_category["avg"]


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
        max_speed_figure = speed_figures_source.get_max_speed_figure(horse.subject_id)
        if max_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return max_speed_figure
