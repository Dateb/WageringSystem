from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import speed_figures_source


class CurrentSpeedFigure(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_speed_figure = speed_figures_source.get_current_speed_figure(horse.name)
        if current_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return current_speed_figure


class BestLifeTimeSpeedFigure(FeatureExtractor):
    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        max_speed_figure = speed_figures_source.get_max_speed_figure(horse.name)
        if max_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return max_speed_figure
