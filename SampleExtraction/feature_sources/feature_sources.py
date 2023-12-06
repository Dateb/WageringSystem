import collections
from abc import abstractmethod, ABC
from collections import deque
from math import sqrt
from sqlite3 import Date
from statistics import mean
from typing import List, Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import compute_speed_figure, race_card_track_to_win_time_track, \
    get_horse_time, get_lengths_per_second, get_velocity
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, SimpleOnlineCalculator, ExponentialOnlineCalculator


CATEGORY_AVERAGE_CALCULATOR = SimpleOnlineCalculator()
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
        if not category["count"]:
            category["prev_avg"] = 0
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days

            category["prev_avg"] = category["avg"]
            category["count"] += 1

            category["avg"] = online_calculator.calculate_average(
                old_average=category["prev_avg"],
                new_obs=new_obs,
                n_days_since_last_obs=n_days_since_last_obs,
                count=category["count"]
            )
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


class HorseNameToSubjectIdSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.names_to_subject_id = {}

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.name not in self.names_to_subject_id:
            self.names_to_subject_id[horse.name] = []

        if str(horse.subject_id) not in self.names_to_subject_id[horse.name]:
            self.names_to_subject_id[horse.name].append(str(horse.subject_id))

    def get_n_ids_of_horse_name(self, horse_name: str) -> int:
        if horse_name not in self.names_to_subject_id:
            return 1

        return len(self.names_to_subject_id[horse_name])


class DistancePreferenceSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.horse_past_form = {}

    def update_horse(self, race_card: RaceCard, horse: Horse):
        horse_id = str(horse.subject_id)

        if horse_id not in self.horse_past_form:
            self.horse_past_form[horse_id] = {}
            self.horse_past_form[horse_id]["distances"] = []
            self.horse_past_form[horse_id]["sp"] = []

        if race_card.distance > 0 and horse.betfair_win_sp > 0:
            self.horse_past_form[horse_id]["distances"].append(race_card.distance)
            self.horse_past_form[horse_id]["sp"].append(horse.betfair_win_sp)

    def get_preference_of_horse(self, race_card: RaceCard, horse: Horse) -> float:
        horse_id = str(horse.subject_id)

        if horse_id not in self.horse_past_form:
            return -1.0

        n_past_distances = len(self.horse_past_form[horse_id]["distances"])
        if n_past_distances < 3:
            return -1.0

        similar_distance_sp = []

        for i in range(n_past_distances):
            past_distance = self.horse_past_form[horse_id]["distances"][i]

            if race_card.distance * 0.9 <= past_distance <= race_card.distance * 1.1:
                similar_distance_sp.append(self.horse_past_form[horse_id]["sp"][i])

        if not similar_distance_sp:
            return -1.0

        return mean(similar_distance_sp) / 1000


class MaxValueSource(FeatureSource, ABC):

    def __init__(self):
        super().__init__()
        self.max_values = nested_dict()
        self.max_value_attribute_groups = []

    def insert_value(self, race_card: RaceCard, horse: Horse, value):
        for attribute_group in self.max_value_attribute_groups:
            attribute_group_key = self.get_attribute_group_key(race_card, horse, attribute_group)

            self.update_max(
                self.max_values[attribute_group_key],
                value,
            )

    def get_attribute_group_key(self, race_card: RaceCard, horse: Horse, attribute_group: List[str]) -> str:
        attribute_group_key = ""
        for attribute in attribute_group:
            if attribute in horse.__dict__:
                attribute_key = getattr(horse, attribute)
            else:
                attribute_key = getattr(race_card, attribute)
            attribute_group_key += f"{attribute_key}_"

        return attribute_group_key[:-1]

    def get_max_of_name(self, name: str) -> float:
        max_elem = self.max_values[name]
        if "max" in max_elem:
            return max_elem["max"]
        return None


class MaxWinProbabilitySource(MaxValueSource):

    def __init__(self):
        super().__init__()
        self.max_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value(race_card, horse, horse.sp_win_prob)


class DrawBiasSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.draw_bias = nested_dict()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        track_name = race_card_track_to_win_time_track(race_card.track_name)
        post_position = str(horse.post_position)
        if post_position != "-1" and horse.horse_distance > 0 and race_card.distance > 0 and race_card.win_time > 0:
            velocity = get_velocity(race_card.win_time, horse.horse_distance, race_card.distance)
            if horse.jockey.weight > 0:
                momentum = velocity * horse.jockey.weight
                self.update_average(
                    self.draw_bias[track_name][post_position],
                    momentum,
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

        if race_card.win_time > 0:
            self.update_track_variant(race_card)

    def update_horse(self, race_card: RaceCard, horse: Horse):
        pass

    def post_update(self, race_card: RaceCard) -> None:
        self.is_first_pre_update = True
        if race_card.race_result is not None and race_card.win_time > 0:
            self.update_base_time(race_card)
            self.update_speed_figures(race_card)
            self.update_par_time(race_card)
            self.update_lengths_per_second(race_card)

    def update_track_variant(self, race_card: RaceCard) -> None:
        par_time = race_card.get_par_time_estimate["avg"]
        win_time = race_card.win_time

        if par_time:
            track_variant = (win_time - par_time) / (win_time + par_time)
            self.update_average(
                category=race_card.track_variant_estimate,
                new_obs=track_variant,
                new_obs_date=race_card.date,
                online_calculator=SimpleOnlineCalculator(),
            )

    def update_base_time(self, race_card: RaceCard):
        win_time = race_card.win_time

        for horse in race_card.runners:
            if horse.horse_distance >= 0:
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
        win_time = race_card.win_time

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
            if not horse.is_scratched and "count" in base_time_estimate and base_time_estimate['count'] > 20:
                base_time_estimate = race_card.get_base_time_estimate(horse.number)
                speed_figure = compute_speed_figure(
                    race_card.race_id,
                    base_time_estimate["avg"],
                    base_time_estimate["std"],
                    race_card.lengths_per_second_estimate["avg"],
                    race_card.win_time,
                    race_card.distance,
                    horse.horse_distance,
                    race_card.track_variant_estimate["avg"],
                )

                if speed_figure is not None:
                    self.update_max(
                        category=self.speed_figures[str(horse.subject_id)],
                        new_obs=speed_figure,
                    )
                    self.update_average(
                        category=self.speed_figures[str(horse.subject_id)],
                        new_obs=speed_figure,
                        new_obs_date=race_card.date,
                        online_calculator=HORSE_SPEED_CALCULATOR,
                    )

    def update_par_time(self, race_card: RaceCard):
        win_time = race_card.win_time

        self.update_average(
            category=race_card.get_par_time_estimate,
            new_obs=win_time,
            new_obs_date=race_card.date,
            online_calculator=PAR_TIME_CALCULATOR,
        )

    def get_current_speed_figure(self, category: str):
        if category not in self.speed_figures:
            return None

        current_speed_figure = self.speed_figures[category]["avg"]
        return current_speed_figure

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


class WindowTimeLengthSource(FeatureSource):

    def __init__(self, window_size=5):
        super().__init__()
        self.window_size = window_size
        self.race_dates_of_horse: Dict[str, collections.deque] = {}

    def update_horse(self, race_card: RaceCard, horse: Horse):
        horse_key = str(horse.subject_id)
        new_race_date = race_card.date

        if horse_key not in self.race_dates_of_horse:
            self.race_dates_of_horse[horse_key] = collections.deque(maxlen=self.window_size)

        self.race_dates_of_horse[horse_key].append(new_race_date)

    def get_day_count_of_window(self, horse: Horse, window_size: int) -> int:
        horse_key = str(horse.subject_id)

        if horse_key not in self.race_dates_of_horse:
            return None

        n_race_dates = len(self.race_dates_of_horse[horse_key])

        if n_race_dates < window_size:
            window_start_date = self.race_dates_of_horse[horse_key][0]
        else:
            window_start_date = self.race_dates_of_horse[horse_key][-window_size]

        window_end_date = self.race_dates_of_horse[horse_key][-1]

        window_day_count = (window_end_date - window_start_date).days

        return window_day_count
