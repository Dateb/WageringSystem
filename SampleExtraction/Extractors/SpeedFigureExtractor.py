import statistics

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Container import SpeedFiguresContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class SpeedFigureExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.base_name = "Speed_Figure"
        self.__speed_figures_container = SpeedFiguresContainer.get_feature_container()
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return f"{self.base_name}_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        n_past_forms = len(form_table.past_forms)

        if self.__n_races_ago > n_past_forms:
            return self.PLACEHOLDER_VALUE

        past_form = form_table.past_forms[self.__n_races_ago - 1]
        past_speed_figure = self.__speed_figures_container.get_speed_figure(past_form)

        if past_speed_figure == -1:
            return self.PLACEHOLDER_VALUE

        return past_speed_figure

    @property
    def container(self) -> FeatureContainer:
        return self.__speed_figures_container
