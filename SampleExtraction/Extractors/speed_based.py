from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import SpeedFiguresSource
from SampleExtraction.Sources.FeatureSource import FeatureSource
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class CurrentSpeedFigure(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = SpeedFiguresSource.get_feature_source()

    def get_name(self) -> str:
        return "Current_Speed_Figure"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_speed_figure = self.source.get_current_speed_figure(horse)
        if current_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return current_speed_figure

    @property
    def container(self) -> FeatureSource:
        return self.source
