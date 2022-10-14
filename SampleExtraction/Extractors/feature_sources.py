from abc import abstractmethod
from math import log
from sqlite3 import Date
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.RawRaceCardInjector import race_card_track_to_win_time_track
from Persistence.JSONPersistence import JSONPersistence
from util.nested_dict import nested_dict


class FeatureSource:

    def __init__(self):
        pass

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float, new_obs_date: Date, base_alpha=0.125) -> None:
        if "avg" not in category:
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days
            average_fade_factor = 0.1 * log(0.1 * n_days_since_last_obs) if n_days_since_last_obs > 10 else 0

            alpha = base_alpha + average_fade_factor

            category["avg"] = alpha * new_obs + (1 - alpha) * category["avg"]
            category["count"] += 1
            category["last_obs_date"] = new_obs_date


class WinRateSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.win_rates = nested_dict()
        self.win_rate_attribute_groups = []

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            for win_rate_attribute_group in self.win_rate_attribute_groups:
                win_rate_total_key = ""
                for win_rate_attribute in win_rate_attribute_group:
                    if win_rate_attribute in horse.__dict__:
                        win_rate_key = getattr(horse, win_rate_attribute)
                    else:
                        win_rate_key = getattr(race_card, win_rate_attribute)
                    win_rate_total_key += f"{win_rate_key}_"

                win_rate_total_key = win_rate_total_key[:-1]
                self.update_average(self.win_rates[win_rate_total_key], horse.has_won, race_card.date)

    def get_win_rate_of_name(self, name: str) -> float:
        win_rate = self.win_rates[name]
        if "avg" in win_rate: #and win_rate["count"] >= 5:
            return win_rate["avg"]
        return -1


class DrawBiasSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__draw_bias = nested_dict()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            post_position = str(horse.post_position)
            if post_position != "-1":
                self.update_average(self.__draw_bias[race_card.track_name][post_position], horse.has_won, race_card.date)

    def draw_bias(self, track_name: str, post_position: int):
        if track_name not in self.__draw_bias or str(post_position) not in self.__draw_bias[track_name]:
            return -1
        return self.__draw_bias[track_name][str(post_position)]["avg"]


class SpeedFiguresSource(FeatureSource):

    BASE_SPEED = 0

    def __init__(self):
        super().__init__()
        self.haha = {}
        self.base_times = nested_dict()
        self.par_figures = nested_dict()
        self.speed_figures = nested_dict()
        self.win_times = JSONPersistence("win_times_contextualized").load()

    def update(self, race_card: RaceCard):
        if race_card.race_result is not None:
            self.compute_base_times(race_card)
            self.compute_points_per_second()
            self.compute_par_figures(race_card)
            self.compute_speed_figures(race_card)

    def get_current_speed_figure(self, horse: Horse):
        if horse.name not in self.speed_figures:
            return -1

        return self.speed_figures[horse.name]["avg"]

    def compute_base_times(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time
        distance_key = str(race_card.distance)

        if win_time > 0:
            self.update_average(category=self.base_times[distance_key], new_obs=win_time, new_obs_date=race_card.date)

    def compute_points_per_second(self):
        for distance in self.base_times:
            self.base_times[distance]["points per second"] = (1 / self.base_times[distance]["avg"]) * 100 * 10

    def compute_par_figures(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time
        distance_key = str(race_card.distance)
        race_class_key = str(race_card.race_class)
        if win_time > 0:
            base_time_of_distance = self.base_times[distance_key]["avg"]
            points_per_second_of_distance = self.base_times[distance_key]["points per second"]
            seconds_difference = base_time_of_distance - win_time
            par_figure = self.BASE_SPEED + seconds_difference * points_per_second_of_distance

            self.update_average(category=self.par_figures[distance_key][race_class_key], new_obs=par_figure, new_obs_date=race_card.date)

    def compute_speed_figures(self, race_card: RaceCard):
        for horse in race_card.horses:
            speed_figure = self.compute_speed_figure(race_card, horse)
            if speed_figure is not None:
                self.update_average(category=self.speed_figures[horse.name], new_obs=speed_figure, new_obs_date=race_card.date)

    def compute_speed_figure(self, race_card: RaceCard, horse: Horse) -> float:
        # TODO: collect more past winning times (distance != 1 check is then not necessary anymore)
        if horse.horse_distance == -1 or race_card.distance == -1:
            return None

        if str(race_card.distance) not in self.base_times:
            return None

        seconds_behind_winner = ((1 / self.get_lengths_per_second(race_card)) * horse.horse_distance)

        horse_time = race_card.race_result.win_time + seconds_behind_winner
        base_time = self.base_times[str(race_card.distance)]["avg"]
        seconds_difference = base_time - horse_time

        points_per_second = self.base_times[str(race_card.distance)]["points per second"]

        track_variant = self.get_track_variant(str(race_card.date), race_card.track_name)

        horse_speed_figure = self.BASE_SPEED + seconds_difference * points_per_second + track_variant

        if horse_speed_figure >= 250:
            horse_speed_figure = 250

        if horse_speed_figure <= -250:
            horse_speed_figure = -250

        return horse_speed_figure

    def get_track_variant(self, date: str, track_name: str):
        track_figure_biases = []

        # TODO: just a quick and dirty mapping. The win times data should rename its track names after the ones on racebets.
        track_name = race_card_track_to_win_time_track(track_name)

        for race in self.win_times[date][track_name]:
            race_distance = str(self.win_times[date][track_name][race]["distance"])

            if race_distance in self.base_times:
                race_class = self.win_times[date][track_name][race]["class"]
                win_time = self.win_times[date][track_name][race]["win_time"]

                if win_time > 0:
                    base_time = self.base_times[race_distance]["avg"]
                    points_per_second = self.base_times[race_distance]["points per second"]

                    seconds_difference = base_time - win_time

                    win_figure = self.BASE_SPEED + seconds_difference * points_per_second
                    if race_class in self.par_figures[race_distance]:
                        par_figure = self.par_figures[race_distance][race_class]["avg"]

                        track_figure_biases.append(par_figure - win_figure)

        if track_figure_biases:
            return sum(track_figure_biases) / len(track_figure_biases)
        else:
            return 0

    def get_lengths_per_second(self, race_card: RaceCard) -> float:
        track_name = race_card_track_to_win_time_track(race_card.track_name)
        if race_card.race_type == "G":
            if race_card.surface == "TRF":
                if race_card.going <= 3:
                    return 6
                if race_card.going >= 4:
                    return 5
            if race_card.surface == "EQT":
                if track_name in ["Kempton", "Lingfield", "Wolverhampton", "Newcastle", "Chelmsford", "Chelmsford City"]:
                    return 6
                if track_name in ["Southwell"]:
                    return 5
                # TODO: Chelmsford and Chelmsford are in the data
                print("length conversion failed:")
                print(track_name)
                print(race_card.race_id)
        if race_card.race_type == "J":
            if race_card.going <= 3:
                return 5
            if race_card.going >= 4:
                return 4
            return 4.5

        return 5.0


#gut-fest: 2.5
#gut: 3
#gut-weich: 3.5
#weich: 4

win_rate_source: WinRateSource = WinRateSource()
speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()
draw_bias_source: DrawBiasSource = DrawBiasSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        win_rate_source, speed_figures_source, draw_bias_source
    ]
