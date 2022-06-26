from datetime import datetime

from SampleExtraction.Container import SpeedFiguresContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class AverageSpeedFigureExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__speed_figures_container = SpeedFiguresContainer.get_feature_container()

    def get_name(self) -> str:
        return "Average_Speed_Figure"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)
        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        speed_figures = []
        past_race_idx = 0
        while past_race_idx < len(form_table) and len(speed_figures) < 5:
            past_race = form_table[past_race_idx]
            race_distance = past_race["raceDistance"]

            if "horseDistance" in past_race and race_distance != -1:
                past_speed_figure = self.__speed_figures_container.get_speed_figure(
                    date=str(datetime.fromtimestamp(past_race["date"]).date()),
                    track=past_race["trackName"],
                    race_distance=race_distance,
                    win_time=past_race["winTimeSeconds"],
                    lengths_behind_winner=past_race["horseDistance"]
                )

                speed_figures.append(past_speed_figure)
            past_race_idx += 1

        if not speed_figures:
            return self.PLACEHOLDER_VALUE

        return sum(speed_figures) / len(speed_figures)

    @property
    def container(self) -> FeatureContainer:
        return self.__speed_figures_container
