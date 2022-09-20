from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import SpeedFiguresSource
from SampleExtraction.Sources.FeatureSource import FeatureSource
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class MaxSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = SpeedFiguresSource.get_feature_source()

    def get_name(self) -> str:
        return "Max_Speed_Figure"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        speed_figures = [
            self.source.get_speed_figure(past_form) for past_form in form_table.past_forms
        ]

        valid_speed_figures = [figure for figure in speed_figures if figure != -1]

        if not valid_speed_figures:
            return self.PLACEHOLDER_VALUE

        return max(valid_speed_figures)

    @property
    def container(self) -> FeatureSource:
        return self.source
