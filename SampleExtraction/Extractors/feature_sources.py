from abc import abstractmethod
from math import log
from sqlite3 import Date
from typing import List

from DataAbstraction.Present.Horse import Horse, speed_dist
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import get_base_time, compute_speed_figure, race_card_track_to_win_time_track
from util.nested_dict import nested_dict


class FeatureSource:

    def __init__(self):
        self.fading_factor = 0.1

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float, new_obs_date: Date, base_alpha=0.125) -> None:
        if not category["avg"]:
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days
            average_fade_factor = self.fading_factor * log(self.fading_factor * n_days_since_last_obs) if n_days_since_last_obs > (1 / self.fading_factor) else 0

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

    def __init__(self):
        super().__init__()
        self.speed_figures = nested_dict()

    def update(self, race_card: RaceCard):
        if race_card.race_result is not None:
            track_name = race_card_track_to_win_time_track(race_card.track_name)
            distance = str(race_card.distance)
            race_class = str(race_card.race_class)

            base_time = get_base_time(track_name, distance, race_class)

            win_time = race_card.race_result.win_time

            if win_time > 0:
                self.update_average(category=base_time, new_obs=win_time, new_obs_date=race_card.date)
                base_time["points per second"] = 1000 / base_time["avg"]
            self.compute_speed_figures(race_card)

    def get_current_speed_figure(self, horse: Horse):
        if horse.name not in self.speed_figures:
            return -1

        return self.speed_figures[horse.name]["avg"]

    def compute_speed_figures(self, race_card: RaceCard):
        for horse in race_card.horses:
            speed_figure = compute_speed_figure(
                str(race_card.date),
                str(race_card.track_name),
                str(race_card.distance),
                str(race_card.race_class),
                race_card.race_result.win_time,
                horse.horse_distance,
                str(race_card.race_type),
                str(race_card.surface),
                race_card.going,
            )

            if speed_figure is not None:
                speed_dist.append(speed_figure)
                self.update_average(
                    category=self.speed_figures[horse.name],
                    new_obs=speed_figure,
                    new_obs_date=race_card.date
                )


win_rate_source: WinRateSource = WinRateSource()
speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()
draw_bias_source: DrawBiasSource = DrawBiasSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        win_rate_source, speed_figures_source, draw_bias_source
    ]
