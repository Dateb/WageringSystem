import statistics

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Container import SpeedFiguresContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class DeviationSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__speed_figures_container = SpeedFiguresContainer.get_feature_container()

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
            past_speed_figure = self.__speed_figures_container.get_speed_figure(past_form)

            if past_speed_figure > 0:
                speed_figures.append(past_speed_figure)
            past_form_idx += 1

        if not speed_figures or len(speed_figures) < 2:
            return self.PLACEHOLDER_VALUE

        return statistics.stdev(speed_figures)

    @property
    def container(self) -> FeatureContainer:
        return self.__speed_figures_container
