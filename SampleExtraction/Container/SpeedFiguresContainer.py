from typing import List

from DataAbstraction.Past.PastForm import PastForm
from DataAbstraction.Present.RaceCard import RaceCard
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
                for past_form in horse.form_table.past_forms:
                    distance_key = str(past_form.distance)

                    win_time = past_form.win_time
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
                for past_form in horse.form_table.past_forms:
                    past_distance = str(past_form.distance)
                    past_class = str(past_form.race_class)

                    win_time = past_form.win_time
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
                    race_distance = str(win_times_contextualized[date][track][race]["distance"])

                    if race_distance in self.__base_times:
                        race_class = win_times_contextualized[date][track][race]["class"]
                        win_time = win_times_contextualized[date][track][race]["win_time"]

                        base_time = self.__base_times[race_distance]["base_time"]
                        points_per_second = self.__base_times[race_distance]["points per second"]

                        seconds_difference = base_time - win_time
                        win_figure = 80 + seconds_difference * points_per_second
                        if race_class in self.__par_figures[race_distance]:
                            par_figure = self.__par_figures[race_distance][race_class]["par_figure"]

                            track_figure_biases.append(par_figure - win_figure)
                if track_figure_biases:
                    self.__track_variants[date][track] = sum(track_figure_biases) / len(track_figure_biases)
                else:
                    self.__track_variants[date][track] = 0

    def get_speed_figure(self, past_form: PastForm) -> float:
        # TODO: collect more past winning times (distance != 1 check is then not necessary anymore)
        if past_form.country != "GB" or past_form.lengths_behind_winner is None or past_form.distance == -1:
            return -1

        seconds_behind_winner = ((1 / self.__get_lengths_per_second(past_form)) * past_form.lengths_behind_winner)
        horse_time = past_form.win_time + seconds_behind_winner

        base_time = self.__base_times[str(past_form.distance)]["base_time"]
        points_per_second = self.__base_times[str(past_form.distance)]["points per second"]

        seconds_difference = base_time - horse_time

        track_variant = self.__track_variants[str(past_form.date)][past_form.track_name]
        horse_speed_figure = 80 + seconds_difference * points_per_second + track_variant
        return horse_speed_figure

    def __get_lengths_per_second(self, past_form: PastForm) -> float:
        if past_form.type == "G":
            if past_form.surface == "TRF":
                if past_form.going <= 3:
                    return 6
                if past_form.going >= 4:
                    return 5
            if past_form.surface == "EQT":
                if past_form.track_name in ["Kempton", "Lingfield", "Wolverhampton", "Chelmsford City", "Newcastle"]:
                    return 6
                if past_form.track_name in ["Southwell"]:
                    return 5
                print(past_form.track_name)
        if past_form.type == "J":
            if past_form.going <= 3:
                return 5
            if past_form.going >= 4:
                return 4
            return 4.5

        return 5.0


#gut-fest: 2.5
#gut: 3
#gut-weich: 3.5
#weich: 4

__feature_container: SpeedFiguresContainer = SpeedFiguresContainer()


def get_feature_container() -> SpeedFiguresContainer:
    return __feature_container
