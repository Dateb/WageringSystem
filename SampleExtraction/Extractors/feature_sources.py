import math
from abc import abstractmethod, ABC
from math import log, sqrt
from sqlite3 import Date
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import get_base_time, compute_speed_figure, race_card_track_to_win_time_track, get_horse_time
from util.nested_dict import nested_dict


class FeatureSource(ABC):

    def __init__(self):
        self.fading_factor = 0.1

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    def preupdate(self, race_cards: List[RaceCard]):
        pass

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float, new_obs_date: Date, base_alpha=0.125, use_fading: bool = True) -> None:
        if not category["avg"]:
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days

            average_fade_factor = 0
            if use_fading:
                average_fade_factor = self.fading_factor * log(self.fading_factor * n_days_since_last_obs) if n_days_since_last_obs > (1 / self.fading_factor) else 0

            alpha = base_alpha + average_fade_factor

            category["avg"] = alpha * new_obs + (1 - alpha) * category["avg"]
            category["count"] += 1
            category["last_obs_date"] = new_obs_date

    def update_variance(self, category: dict, new_obs: float):
        if not category["count"]:
            category["variance"] = 0
        else:
            n = category["count"]

            variance = 0
            if n >= 2:
                old_variance = category["variance"]
                variance += (n - 2) * old_variance / (n - 1)

            variance += (1 / n) * (new_obs - category["avg"]) * (new_obs - category["avg"])

            category["variance"] = variance

    def update_max(self, category: dict, new_obs: float) -> None:
        if not category["max"] or new_obs > category["max"]:
            category["max"] = new_obs


class CategoryAverageSource(FeatureSource, ABC):
    def __init__(self):
        super().__init__()
        self.averages = nested_dict()
        self.average_attribute_groups = []

    def insert_value_into_avg(self, race_card: RaceCard, horse: Horse, value):
        for win_rate_attribute_group in self.average_attribute_groups:
            win_rate_total_key = ""
            for win_rate_attribute in win_rate_attribute_group:
                if win_rate_attribute in horse.__dict__:
                    win_rate_key = getattr(horse, win_rate_attribute)
                else:
                    win_rate_key = getattr(race_card, win_rate_attribute)
                win_rate_total_key += f"{win_rate_key}_"

            win_rate_total_key = win_rate_total_key[:-1]
            self.update_average(self.averages[win_rate_total_key], value, race_card.date)

    def get_average_of_name(self, name: str) -> float:
        average_elem = self.averages[name]
        if "avg" in average_elem:
            return average_elem["avg"]
        return -1


class WinRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.insert_value_into_avg(race_card, horse, horse.has_won)


class ShowRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            show_indicator = int(1 <= horse.place <= 3)
            self.insert_value_into_avg(race_card, horse, show_indicator)


class PurseRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.insert_value_into_avg(race_card, horse, horse.purse)


class PercentageBeatenSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update(self, race_card: RaceCard):
        n_horses = race_card.n_horses
        for horse in race_card.horses:
            # TODO: n_horses is 1 sometimes. This should be looked into
            if horse.place >= 1 and n_horses >= 2:
                percentage_beaten = (n_horses - horse.place) / (n_horses - 1)
                self.insert_value_into_avg(race_card, horse, percentage_beaten)


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
        self.track_variants = nested_dict()

    def preupdate(self, race_cards: List[RaceCard]):
        self.track_variants = nested_dict()
        for race_card in race_cards:
            track_name = race_card_track_to_win_time_track(race_card.track_name)
            for horse in race_card.horses:
                current_horse_speed = self.get_current_speed_figure(horse.name)
                if current_horse_speed != -1:
                    next_horse_speed = compute_speed_figure(
                        str(race_card.date),
                        str(race_card.track_name),
                        race_card.distance,
                        race_card.race_result.win_time,
                        horse.horse_distance,
                        str(race_card.race_type),
                        str(race_card.race_type_detail),
                        str(race_card.surface),
                        race_card.going,
                    )
                    if next_horse_speed is not None:
                        current_percentile = .5 * (math.erf(current_horse_speed / 2 ** .5) + 1)
                        next_percentile = .5 * (math.erf(next_horse_speed / 2 ** .5) + 1)
                        track_variant = next_percentile - current_percentile
                        if "avg" in self.track_variants[track_name]:
                            n = self.track_variants[track_name]["count"]
                            old_avg = self.track_variants[track_name]["avg"]
                            self.track_variants[track_name]["avg"] = (n * old_avg + track_variant) / (n + 1)
                            self.track_variants[track_name]["count"] += 1
                        else:
                            self.track_variants[track_name]["avg"] = track_variant
                            self.track_variants[track_name]["count"] = 1

    def update(self, race_card: RaceCard):
        if race_card.race_result is not None:
            track_name = race_card_track_to_win_time_track(race_card.track_name)
            distance = str(race_card.distance)
            race_type_detail = str(race_card.race_type_detail)

            base_time = get_base_time(track_name, distance, race_type_detail)

            win_time = race_card.race_result.win_time

            if win_time > 0:
                for horse in race_card.horses:
                    horse_time = get_horse_time(
                        win_time,
                        track_name,
                        str(race_card.race_type),
                        str(race_card.surface),
                        race_card.going,
                        horse.horse_distance,
                    )
                    self.update_average(category=base_time, new_obs=horse_time, new_obs_date=race_card.date, base_alpha=0.0001, use_fading=False)
                    self.update_variance(category=base_time, new_obs=horse_time)
            self.compute_speed_figures(race_card)

    def get_current_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return -1

        return self.speed_figures[category]["avg"]

    def get_max_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return -1

        return self.speed_figures[category]["max"]

    def compute_speed_figures(self, race_card: RaceCard):
        for horse in race_card.horses:
            speed_figure = compute_speed_figure(
                str(race_card.date),
                str(race_card.track_name),
                race_card.distance,
                race_card.race_result.win_time,
                horse.horse_distance,
                str(race_card.race_type),
                str(race_card.race_type_detail),
                str(race_card.surface),
                race_card.going,
            )

            if speed_figure is not None:
                track_name = race_card_track_to_win_time_track(race_card.track_name)

                if track_name in self.track_variants:
                    speed_figure = (1 - self.track_variants[track_name]["avg"]) * speed_figure

                self.update_average(
                    category=self.speed_figures[horse.name],
                    new_obs=speed_figure,
                    new_obs_date=race_card.date,
                )
                self.update_max(
                    category=self.speed_figures[horse.name],
                    new_obs=speed_figure,
                )


win_rate_source: WinRateSource = WinRateSource()
show_rate_source: ShowRateSource = ShowRateSource()
purse_rate_source: PurseRateSource = PurseRateSource()
percentage_beaten_source: PercentageBeatenSource = PercentageBeatenSource()
speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()
draw_bias_source: DrawBiasSource = DrawBiasSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        win_rate_source, show_rate_source, purse_rate_source, percentage_beaten_source, speed_figures_source, draw_bias_source
    ]
