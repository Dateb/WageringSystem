import math
from abc import abstractmethod, ABC
from math import sqrt
from sqlite3 import Date
from statistics import mean
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import get_base_time, compute_speed_figure, race_card_track_to_win_time_track, \
    get_horse_time, get_speed
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, SimpleOnlineCalculator, ExponentialOnlineCalculator


CATEGORY_AVERAGE_CALCULATOR = ExponentialOnlineCalculator(fading_factor=0.1)
BASE_TIME_CALCULATOR = ExponentialOnlineCalculator(fading_factor=0.1)
HORSE_SPEED_CALCULATOR = ExponentialOnlineCalculator(fading_factor=0.1)
TRACK_SPEED_CALCULATOR = SimpleOnlineCalculator()
DRAW_BIAS_CALCULATOR = ExponentialOnlineCalculator(base_alpha=0.001, fading_factor=0.1)


class FeatureSource(ABC):

    def __init__(self):
        pass

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float, new_obs_date: Date, online_calculator: OnlineCalculator) -> None:
        if not category["avg"]:
            category["prev_avg"] = 0
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days

            category["prev_avg"] = category["avg"]
            category["avg"] = online_calculator.calculate_average(
                old_average=category["avg"],
                new_obs=new_obs,
                count=category["count"],
                n_days_since_last_obs=n_days_since_last_obs,
            )
            category["count"] += 1
            category["last_obs_date"] = new_obs_date

    def update_variance(self, category: dict, new_obs: float):
        if not category["count"]:
            category["variance"] = 0
            category["std"] = 0
        else:
            n = category["count"]

            variance = 0
            if n >= 2:
                old_variance = category["variance"]
                variance += (n - 2) * old_variance / (n - 1)

            variance += (1 / n) * (new_obs - category["prev_avg"]) * (new_obs - category["prev_avg"])

            category["variance"] = variance
            category["std"] = sqrt(category["variance"])

    def update_max(self, category: dict, new_obs: float) -> None:
        if not category["max"] or new_obs > category["max"]:
            category["max"] = new_obs

    def update_previous(self, category: dict, new_obs: float) -> None:
        category["previous"] = new_obs


class CategoryAverageSource(FeatureSource, ABC):
    def __init__(self):
        super().__init__()
        self.averages = nested_dict()
        self.average_attribute_groups = []

    def insert_value_into_avg(self, race_card: RaceCard, horse: Horse, value):
        for attribute_group in self.average_attribute_groups:
            attribute_group_key = ""
            for attribute in attribute_group:
                if attribute in horse.__dict__:
                    attribute_key = getattr(horse, attribute)
                else:
                    attribute_key = getattr(race_card, attribute)
                attribute_group_key += f"{attribute_key}_"

            attribute_group_key = attribute_group_key[:-1]
            self.update_average(
                self.averages[attribute_group_key],
                value,
                race_card.date,
                CATEGORY_AVERAGE_CALCULATOR,
            )

    def get_average_of_name(self, name: str) -> float:
        average_elem = self.averages[name]
        if "avg" in average_elem:
            return average_elem["avg"]
        return -1


class PreviousValueSource(FeatureSource, ABC):
    def __init__(self):
        super().__init__()
        self.previous_values = nested_dict()
        self.previous_value_attribute_groups = []

    def insert_previous_value(self, race_card: RaceCard, horse: Horse, value):
        for attribute_group in self.previous_value_attribute_groups:
            attribute_group_key = ""
            for attribute in attribute_group:
                if attribute in horse.__dict__:
                    attribute_key = getattr(horse, attribute)
                else:
                    attribute_key = getattr(race_card, attribute)
                attribute_group_key += f"{attribute_key}_"

            attribute_group_key = attribute_group_key[:-1]
            self.update_previous(
                self.previous_values[attribute_group_key],
                value,
            )

    def get_previous_of_name(self, name: str) -> float:
        previous_elem = self.previous_values[name]
        if "previous" in previous_elem:
            return previous_elem["previous"]
        return -1


class PreviousDistanceSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.insert_previous_value(race_card, horse, race_card.distance)


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
        self.draw_bias = nested_dict()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            track_name = race_card_track_to_win_time_track(race_card.track_name)
            post_position = str(horse.post_position)
            if post_position != "-1":
                self.update_average(
                    self.draw_bias[track_name][post_position],
                    horse.relevance,
                    race_card.date,
                    DRAW_BIAS_CALCULATOR,
                )

    def get_draw_bias(self, track_name: str, post_position: int):
        if track_name not in self.draw_bias or str(post_position) not in self.draw_bias[track_name]:
            return -1
        return self.draw_bias[track_name][str(post_position)]["avg"]


class SpeedFiguresSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.speed_figures = nested_dict()
        self.track_variants = nested_dict()

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    def update(self, race_card: RaceCard):
        if race_card.race_result is not None:
            self.update_track_speed(race_card)
            self.update_base_time(race_card)
            self.update_speed_figures(race_card)

    def update_base_time(self, race_card: RaceCard):
        win_time_track = race_card_track_to_win_time_track(race_card.track_name)
        distance = str(race_card.distance)
        track_surface = race_card.surface
        going = str(race_card.going)
        race_type_detail = str(race_card.race_type_detail)

        base_time = get_base_time(win_time_track, distance, track_surface, going, race_type_detail)

        win_time = race_card.race_result.win_time

        if win_time > 0:
            horse_times = [get_horse_time(
                win_time,
                win_time_track,
                distance,
                track_surface,
                going,
                race_type_detail,
                horse.horse_distance,
            ) for horse in race_card.horses if horse.horse_distance >= 0]
            if horse_times:
                mean_horse_time = mean(horse_times)
                self.update_average(
                    category=base_time,
                    new_obs=mean_horse_time,
                    new_obs_date=race_card.date,
                    online_calculator=BASE_TIME_CALCULATOR,
                )
                self.update_variance(category=base_time, new_obs=mean_horse_time)

    def update_track_speed(self, race_card: RaceCard):
        win_time_track = race_card_track_to_win_time_track(race_card.track_name)
        distance = str(race_card.distance)
        track_surface = race_card.surface
        going = str(race_card.going)
        race_type_detail = str(race_card.race_type_detail)

        track_speed = get_speed(win_time_track, distance, track_surface, going, race_type_detail)

        win_time = race_card.race_result.win_time

        if win_time > 0:
            self.update_average(
                category=track_speed,
                new_obs=win_time,
                new_obs_date=race_card.date,
                online_calculator=TRACK_SPEED_CALCULATOR,
            )

    def update_speed_figures(self, race_card: RaceCard):
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
                # track_name = race_card_track_to_win_time_track(race_card.track_name)

                # if track_name in self.track_variants:
                #     speed_figure = speed_figure - self.track_variants[track_name]["avg"]

                self.update_average(
                    category=self.speed_figures[horse.name],
                    new_obs=speed_figure,
                    new_obs_date=race_card.date,
                    online_calculator=HORSE_SPEED_CALCULATOR,
                )
                self.update_max(
                    category=self.speed_figures[horse.name],
                    new_obs=speed_figure,
                )

    def get_current_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return -1

        current_speed_figure = self.speed_figures[category]["avg"]
        return current_speed_figure

    def get_max_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return -1

        return self.speed_figures[category]["max"]


# Average based sources:
win_rate_source: WinRateSource = WinRateSource()
show_rate_source: ShowRateSource = ShowRateSource()
purse_rate_source: PurseRateSource = PurseRateSource()
percentage_beaten_source: PercentageBeatenSource = PercentageBeatenSource()

#Previous value based sources:
previous_distance_source: PreviousDistanceSource = PreviousDistanceSource()

speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()

draw_bias_source: DrawBiasSource = DrawBiasSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        win_rate_source, show_rate_source, purse_rate_source, percentage_beaten_source,

        previous_distance_source,

        speed_figures_source,

        draw_bias_source,
    ]
