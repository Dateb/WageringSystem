import statistics

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import SpeedFiguresSource
from SampleExtraction.Sources.FeatureSource import FeatureSource
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class DeviationSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.source = SpeedFiguresSource.get_speed_figures_source()

    def get_name(self) -> str:
        return "Deviation_Speed_Figure"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        n_past_forms = len(form_table.past_forms)

        if n_past_forms == 0:
            return self.PLACEHOLDER_VALUE

        speed_figures = []
        past_form_idx = 0
        while past_form_idx < n_past_forms and len(speed_figures) < 5:
            past_form = form_table.get(past_form_idx)
            past_speed_figure = self.source.__get_speed_figure(past_form)

            if past_speed_figure != -1:
                speed_figures.append(past_speed_figure)
            past_form_idx += 1

        if not speed_figures or len(speed_figures) < 2:
            return self.PLACEHOLDER_VALUE

        return statistics.stdev(speed_figures)

    @property
    def container(self) -> FeatureSource:
        return self.source
