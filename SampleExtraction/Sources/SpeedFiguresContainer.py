from typing import List

from DataAbstraction.Past.PastForm import PastForm
from DataAbstraction.Present.RaceCard import RaceCard
from Persistence.JSONPersistence import JSONPersistence
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class SpeedFiguresContainer(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__base_times = nested_dict()
        self.__par_figures = nested_dict()
        self.__win_times = JSONPersistence("win_times_contextualized").load()

    def update(self, race_card: RaceCard):
        self.__compute_base_times(race_card)
        self.__compute_points_per_second()
        self.__compute_par_figures(race_card)

    def __compute_base_times(self, race_card: RaceCard):
        for horse in race_card.horses:
            for past_form in horse.form_table.past_forms:
                distance_key = str(past_form.distance)

                win_time = past_form.win_time
                if win_time > 0:
                    self.update_average(category=self.__base_times[distance_key], new_obs=win_time)

    def __compute_points_per_second(self):
        for distance in self.__base_times:
            self.__base_times[distance]["points per second"] = (1 / self.__base_times[distance]["base_time"]) * 100 * 10

    def __compute_par_figures(self, race_card: RaceCard):
        # TODO: dont use past form winning times to estimate par figures
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

                    self.update_average(category=self.__par_figures[past_distance][past_class], new_obs=par_figure)

    def get_speed_figure(self, past_form: PastForm) -> float:
        # TODO: collect more past winning times (distance != 1 check is then not necessary anymore)
        if past_form.country != "GB" or past_form.lengths_behind_winner == -1 or past_form.distance == -1:
            return -1

        if str(past_form.distance) not in self.__base_times:
            return -1

        seconds_behind_winner = ((1 / self.__get_lengths_per_second(past_form)) * past_form.lengths_behind_winner)
        horse_time = past_form.win_time + seconds_behind_winner

        base_time = self.__base_times[str(past_form.distance)]["base_time"]
        points_per_second = self.__base_times[str(past_form.distance)]["points per second"]

        seconds_difference = base_time - horse_time

        track_variant = self.__get_track_variant(str(past_form.date), past_form.track_name)
        horse_speed_figure = 80 + seconds_difference * points_per_second + track_variant
        return horse_speed_figure

    def __get_track_variant(self, date: str, track: str):
        track_figure_biases = []

        for race in self.__win_times[date][track]:
            race_distance = str(self.__win_times[date][track][race]["distance"])

            if race_distance in self.__base_times:
                race_class = self.__win_times[date][track][race]["class"]
                win_time = self.__win_times[date][track][race]["win_time"]

                base_time = self.__base_times[race_distance]["base_time"]
                points_per_second = self.__base_times[race_distance]["points per second"]

                seconds_difference = base_time - win_time
                win_figure = 80 + seconds_difference * points_per_second
                if race_class in self.__par_figures[race_distance]:
                    par_figure = self.__par_figures[race_distance][race_class]["par_figure"]

                    track_figure_biases.append(par_figure - win_figure)

        if track_figure_biases:
            return sum(track_figure_biases) / len(track_figure_biases)
        else:
            return 0

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
