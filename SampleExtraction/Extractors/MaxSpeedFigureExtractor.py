from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Container import SpeedFiguresContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class MaxSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__speed_figures_container = SpeedFiguresContainer.get_feature_container()

    def get_name(self) -> str:
        return "Max_Speed_Figure"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        speed_figures = [
            self.__speed_figures_container.get_speed_figure(past_form) for past_form in form_table.past_forms
        ]

        valid_speed_figures = [figure for figure in speed_figures if figure > 0]

        if not valid_speed_figures:
            return self.PLACEHOLDER_VALUE

        return max(valid_speed_figures)

    @property
    def container(self) -> FeatureContainer:
        return self.__speed_figures_container
