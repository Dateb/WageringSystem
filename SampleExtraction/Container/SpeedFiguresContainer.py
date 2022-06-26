from typing import List

from DataAbstraction.RaceCard import RaceCard
from Persistence.JSONPersistence import JSONPersistence
from SampleExtraction.Container.FeatureContainer import FeatureContainer


class SpeedFiguresContainer(FeatureContainer):

    def __init__(self):
        super().__init__()
        self.__base_times = {}
        self.__par_figures = {}
        self.__track_variants = {}

    def fit(self, train_race_cards: List[RaceCard]):
        self.__compute_base_times(train_race_cards)
        self.__compute_points_per_second()
        self.__compute_par_figures(train_race_cards)
        self.__compute_track_variants()

    def __compute_base_times(self, train_race_cards: List[RaceCard]):
        for race_card in train_race_cards:
            for horse in race_card.horses:
                for past_race in race_card.form_table_of_horse(horse):
                    distance_key = str(past_race["raceDistance"])

                    win_time = past_race["winTimeSeconds"]
                    if win_time > 0:
                        if distance_key not in self.__base_times:
                            self.__base_times[distance_key] = {"base_time": win_time, "count": 1}
                        else:
                            self.__base_times[distance_key]["count"] += 1
                            new_count = self.__base_times[distance_key]["count"]
                            old_avg = self.__base_times[distance_key]["base_time"]

                            new_avg = old_avg + (win_time - old_avg) / new_count
                            self.__base_times[distance_key]["base_time"] = new_avg

    def __compute_points_per_second(self):
        for distance in self.__base_times:
            self.__base_times[distance]["points per second"] = (1 / self.__base_times[distance]["base_time"]) * 100 * 10

    def __compute_par_figures(self, train_race_cards: List[RaceCard]):
        for race_card in train_race_cards:
            for horse in race_card.horses:
                for past_race in race_card.form_table_of_horse(horse):
                    past_distance = str(past_race["raceDistance"])
                    past_class = str(past_race["categoryLetter"])

                    win_time = past_race["winTimeSeconds"]
                    if win_time > 0:
                        base_time_of_distance = self.__base_times[past_distance]["base_time"]
                        points_per_second_of_distance = self.__base_times[past_distance]["points per second"]
                        seconds_difference = base_time_of_distance - win_time
                        par_figure = 80 + seconds_difference * points_per_second_of_distance
                        if past_distance not in self.__par_figures:
                            self.__par_figures[past_distance] = {past_class: {"par_figure": par_figure, "count": 1}}
                        if past_class not in self.__par_figures[past_distance]:
                            self.__par_figures[past_distance][past_class] = {"par_figure": par_figure, "count": 1}
                        else:
                            self.__par_figures[past_distance][past_class]["count"] += 1
                            new_count = self.__par_figures[past_distance][past_class]["count"]
                            old_avg = self.__par_figures[past_distance][past_class]["par_figure"]

                            new_avg = old_avg + (par_figure - old_avg) / new_count
                            self.__par_figures[past_distance][past_class]["par_figure"] = new_avg

    def __compute_track_variants(self):
        win_times_contextualized = JSONPersistence("win_times_contextualized").load()

        for date in win_times_contextualized:
            self.__track_variants[date] = {}
            for track in win_times_contextualized[date]:
                track_figure_biases = []
                for race in win_times_contextualized[date][track]:
                    race_distance = win_times_contextualized[date][track][race]["distance"]
                    race_class = win_times_contextualized[date][track][race]["class"]
                    win_time = win_times_contextualized[date][track][race]["win_time"]

                    base_time = self.__base_times[str(race_distance)]["base_time"]
                    points_per_second = self.__base_times[str(race_distance)]["points per second"]

                    seconds_difference = base_time - win_time
                    win_figure = 80 + seconds_difference * points_per_second
                    if race_class in self.__par_figures[str(race_distance)]:
                        par_figure = self.__par_figures[str(race_distance)][race_class]["par_figure"]

                        track_figure_biases.append(par_figure - win_figure)
                if track_figure_biases:
                    self.__track_variants[date][track] = sum(track_figure_biases) / len(track_figure_biases)
                else:
                    self.__track_variants[date][track] = 0

    def get_speed_figure(self, date: str, track: str, race_distance: int, win_time: float, lengths_behind_winner: float) -> float:
        horse_time = win_time + (0.2 * lengths_behind_winner)

        base_time = self.__base_times[str(race_distance)]["base_time"]
        points_per_second = self.__base_times[str(race_distance)]["points per second"]

        seconds_difference = base_time - horse_time
        horse_speed_figure = 80 + seconds_difference * points_per_second + self.__track_variants[date][track]
        return horse_speed_figure


__feature_container: SpeedFiguresContainer = SpeedFiguresContainer()


def get_feature_container() -> SpeedFiguresContainer:
    return __feature_container
