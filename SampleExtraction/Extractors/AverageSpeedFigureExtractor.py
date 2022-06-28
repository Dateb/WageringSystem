from datetime import datetime

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Container import SpeedFiguresContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AverageSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__speed_figures_container = SpeedFiguresContainer.get_feature_container()

    def get_name(self) -> str:
        return "Average_Speed_Figure"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        n_past_forms = len(form_table.past_forms)
        speed_figures = []
        past_form_idx = 0
        while past_form_idx < n_past_forms and len(speed_figures) < 5:
            past_form = form_table.get(past_form_idx)
            race_distance = past_form.distance

            if past_form.lengths_behind_winner is not None and race_distance != -1:
                past_speed_figure = self.__speed_figures_container.get_speed_figure(
                    date=str(past_form.date),
                    track=past_form.track_name,
                    race_distance=race_distance,
                    win_time=past_form.win_time,
                    lengths_behind_winner=past_form.lengths_behind_winner,
                )

                speed_figures.append(past_speed_figure)
            past_form_idx += 1

        if not speed_figures:
            return self.PLACEHOLDER_VALUE

        return sum(speed_figures) / len(speed_figures)

    @property
    def container(self) -> FeatureContainer:
        return self.__speed_figures_container
