from abc import abstractmethod, ABC
from collections import deque
from math import sqrt
from sqlite3 import Date
from statistics import mean
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import compute_speed_figure, race_card_track_to_win_time_track, \
    get_horse_time, get_lengths_per_second, is_horse_distance_too_far_from_winner
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, SimpleOnlineCalculator, ExponentialOnlineCalculator


CATEGORY_AVERAGE_CALCULATOR = ExponentialOnlineCalculator(fading_factor=0.1)
BASE_TIME_CALCULATOR = ExponentialOnlineCalculator(window_size=100, fading_factor=0.1)
HORSE_SPEED_CALCULATOR = ExponentialOnlineCalculator(fading_factor=0.1)
LENGTH_MODIFIER_CALCULATOR = ExponentialOnlineCalculator(window_size=100, fading_factor=0.1)
PAR_TIME_CALCULATOR = ExponentialOnlineCalculator(window_size=100, fading_factor=0.1)
DRAW_BIAS_CALCULATOR = ExponentialOnlineCalculator(window_size=1000, fading_factor=0.1)


class FeatureSource(ABC):

    def __init__(self):
        pass

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.post_update(race_card)

    def pre_update(self, race_card: RaceCard):
        pass

    def post_update(self, race_card: RaceCard):
        for horse in race_card.horses:
            if not horse.is_scratched:
                self.update_horse(race_card, horse)

    @abstractmethod
    def update_horse(self, race_card: RaceCard, horse: Horse):
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
                old_average=category["prev_avg"],
                new_obs=new_obs,
                n_days_since_last_obs=n_days_since_last_obs,
                count=category["count"]
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
        if "avg" in average_elem and average_elem["count"] >= 3:
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


class PreviousWinProbSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        previous_win_prob = (1 / horse.racebets_win_sp) * (1 / race_card.overround)
        self.insert_previous_value(race_card, horse, previous_win_prob)


class PreviousDistanceSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.distance)


class PreviousTrainerSource(PreviousValueSource):
    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.trainer_name)


class WinRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, horse.has_won)


class ShowRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        show_indicator = int(1 <= horse.place <= 3)
        self.insert_value_into_avg(race_card, horse, show_indicator)


class PurseRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, horse.purse)


class PercentageBeatenSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        n_horses = race_card.n_horses

        # TODO: n_horses is 1 sometimes. This should be looked into
        if horse.place >= 1 and n_horses >= 2:
            percentage_beaten = (n_horses - horse.place) / (n_horses - 1)
            self.insert_value_into_avg(race_card, horse, percentage_beaten)


class DrawBiasSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.draw_bias = nested_dict()

    def update_horse(self, race_card: RaceCard, horse: Horse):
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
        self.is_first_pre_update = True

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.post_update(race_card)

    def pre_update(self, race_card: RaceCard) -> None:
        if self.is_first_pre_update:
            RaceCard.reset_track_variant_estimate()
            self.is_first_pre_update = False

        if race_card.race_result is not None:
            self.update_track_variant(race_card)

    def update_horse(self, race_card: RaceCard, horse: Horse):
        pass

    def post_update(self, race_card: RaceCard) -> None:
        self.is_first_pre_update = True
        if race_card.race_result is not None and race_card.race_result.win_time > 0:
            self.update_base_time(race_card)
            self.update_speed_figures(race_card)
            self.update_par_time(race_card)
            self.update_lengths_per_second(race_card)

    def update_track_variant(self, race_card: RaceCard) -> None:
        par_time = race_card.get_par_time_estimate["avg"]
        win_time = race_card.race_result.win_time

        if par_time:
            track_variant = (win_time - par_time) / (win_time + par_time)
            self.update_average(
                category=race_card.track_variant_estimate,
                new_obs=track_variant,
                new_obs_date=race_card.date,
                online_calculator=SimpleOnlineCalculator(),
            )

    def update_base_time(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time

        for horse in race_card.runners:
            if horse.horse_distance >= 0 and is_horse_distance_too_far_from_winner(race_card.distance, horse.horse_distance):
                horse_time = get_horse_time(
                    win_time,
                    race_card.lengths_per_second_estimate["avg"],
                    horse.horse_distance,
                )
                base_time_estimate = race_card.get_base_time_estimate(horse.number)
                self.update_average(
                    category=base_time_estimate,
                    new_obs=horse_time,
                    new_obs_date=race_card.date,
                    online_calculator=BASE_TIME_CALCULATOR,
                )
                self.update_variance(category=base_time_estimate, new_obs=horse_time)

    def update_lengths_per_second(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time

        lengths_per_second = get_lengths_per_second(race_card.distance, win_time)

        self.update_average(
            category=race_card.lengths_per_second_estimate,
            new_obs=lengths_per_second,
            new_obs_date=race_card.date,
            online_calculator=LENGTH_MODIFIER_CALCULATOR,
        )

    def update_speed_figures(self, race_card: RaceCard):
        for horse in race_card.horses:
            base_time_estimate = race_card.get_base_time_estimate(horse.number)
            if not horse.is_scratched and "count" in base_time_estimate and base_time_estimate['count'] > 200:
                base_time_estimate = race_card.get_base_time_estimate(horse.number)
                speed_figure = compute_speed_figure(
                    race_card.race_id,
                    base_time_estimate["avg"],
                    base_time_estimate["std"],
                    race_card.lengths_per_second_estimate["avg"],
                    race_card.race_result.win_time,
                    race_card.distance,
                    horse.horse_distance,
                    race_card.track_variant_estimate["avg"],
                )

                if speed_figure is not None:
                    self.update_max(
                        category=self.speed_figures[horse.subject_id],
                        new_obs=speed_figure,
                    )
                    self.update_average(
                        category=self.speed_figures[horse.subject_id],
                        new_obs=speed_figure,
                        new_obs_date=race_card.date,
                        online_calculator=HORSE_SPEED_CALCULATOR,
                    )

    def update_par_time(self, race_card: RaceCard):
        win_time = race_card.race_result.win_time

        self.update_average(
            category=race_card.get_par_time_estimate,
            new_obs=win_time,
            new_obs_date=race_card.date,
            online_calculator=PAR_TIME_CALCULATOR,
        )

    def get_current_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return -1

        current_speed_figure = self.speed_figures[category]["avg"]
        return current_speed_figure + 100

    def get_max_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return 0

        return self.speed_figures[category]["max"]


class HasFallenSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.has_fallen = nested_dict()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.previous_performance == "UR":
            self.has_fallen[horse.subject_id] = True

    def get_has_fallen(self, horse: Horse) -> bool:
        if horse.subject_id not in self.has_fallen:
            self.has_fallen[horse.subject_id] = False
            return False
        return self.has_fallen[horse.subject_id]


# Average based sources:
win_rate_source: WinRateSource = WinRateSource()
show_rate_source: ShowRateSource = ShowRateSource()
purse_rate_source: PurseRateSource = PurseRateSource()
percentage_beaten_source: PercentageBeatenSource = PercentageBeatenSource()

#Previous value based sources:
previous_win_prob_source: PreviousWinProbSource = PreviousWinProbSource()
previous_distance_source: PreviousDistanceSource = PreviousDistanceSource()
previous_trainer_source: PreviousTrainerSource = PreviousTrainerSource()

speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()

draw_bias_source: DrawBiasSource = DrawBiasSource()

has_fallen_source: HasFallenSource = HasFallenSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        win_rate_source, show_rate_source, purse_rate_source, percentage_beaten_source,

        previous_win_prob_source, previous_distance_source, previous_trainer_source,

        speed_figures_source,

        draw_bias_source,

        has_fallen_source,
    ]
