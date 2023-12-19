import collections
from abc import abstractmethod, ABC
from collections import deque
from datetime import date
from math import sqrt
from sqlite3 import Date
from statistics import mean
from typing import List, Dict, Callable

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from util.speed_calculator import compute_speed_figure, race_card_track_to_win_time_track, \
    get_horse_time, get_lengths_per_second
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, SimpleOnlineCalculator, ExponentialOnlineCalculator


CATEGORY_AVERAGE_CALCULATOR = SimpleOnlineCalculator()
PAR_MOMENTUM_CALCULATOR = ExponentialOnlineCalculator(window_size=1000)
DRAW_BIAS_CALCULATOR = ExponentialOnlineCalculator(window_size=1000)


class FeatureValueGroup:

    attributes: List[str]
    value_calculator: Callable[[RaceCard, Horse], float]

    def __init__(self, attributes: List[str], value_calculator: Callable[[RaceCard, Horse], float]):
        self.attributes = attributes
        self.value_calculator = value_calculator
        self.value_name = value_calculator.__name__

    def get_key(self, race_card: RaceCard, horse: Horse) -> str:
        key = ""
        for attribute in self.attributes:
            if attribute in horse.__dict__:
                attribute_key = getattr(horse, attribute)
            else:
                attribute_key = getattr(race_card, attribute)
            key += f"{attribute_key}_"

        key += self.value_name
        return key

    @property
    def name(self) -> str:
        return f"{self.attributes}/{self.value_name}"


class FeatureSource(ABC):

    def __init__(self):
        self.feature_values = nested_dict()
        self.feature_value_groups: List[FeatureValueGroup] = []
        self.feature_value_group_names: List[str] = []

    def register_feature_value_group(self, feature_value_group: FeatureValueGroup):
        if feature_value_group.name not in self.feature_value_group_names:
            self.feature_value_groups.append(feature_value_group)
            self.feature_value_group_names.append(feature_value_group.name)

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.post_update(race_card)

    def pre_update(self, race_card: RaceCard):
        pass

    def post_update(self, race_card: RaceCard):
        for horse in race_card.horses:
            if not horse.is_scratched:
                self.update_horse(race_card, horse)

    def update_horse(self, race_card: RaceCard, horse: Horse):
        for feature_value_group in self.feature_value_groups:
            feature_value_group_key = feature_value_group.get_key(race_card, horse)
            new_feature_value = feature_value_group.value_calculator(race_card, horse)

            self.update_statistic(self.feature_values[feature_value_group_key], new_feature_value, race_card.date)

    def get_feature_value(self, race_card: RaceCard, horse: Horse, feature_value_group: FeatureValueGroup) -> float:
        feature_value_group_key = feature_value_group.get_key(race_card, horse)
        feature_value_group = self.feature_values[feature_value_group_key]
        if "value" in feature_value_group:
            return feature_value_group["value"]
        return None

    @abstractmethod
    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        pass

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

    def get_name(self) -> str:
        return self.__class__.__name__


class PreviousValueSource(FeatureSource):
    def __init__(self):
        super().__init__()

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        category["value"] = new_feature_value


class AverageValueSource(FeatureSource):

    def __init__(self, window_size=5, min_obs_thresh=3):
        super().__init__()
        self.window_size = window_size
        self.average_calculator = ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.0)
        self.min_obs_thresh = min_obs_thresh

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        if not category["count"]:
            category["prev_avg"] = 0
            category["value"] = new_feature_value
            category["count"] = 1
            category["last_obs_date"] = value_date
        else:
            n_days_since_last_obs = (value_date - category["last_obs_date"]).days

            category["prev_avg"] = category["value"]
            category["count"] += 1

            category["value"] = self.average_calculator.calculate_average(
                old_average=category["prev_avg"],
                new_obs=new_feature_value,
                n_days_since_last_obs=n_days_since_last_obs,
                count=category["count"]
            )
            category["last_obs_date"] = value_date

    def get_feature_value(self, race_card: RaceCard, horse: Horse, feature_value_group: FeatureValueGroup) -> float:
        feature_value_group_key = feature_value_group.get_key(race_card, horse)
        feature_value_group = self.feature_values[feature_value_group_key]
        if "value" in feature_value_group and feature_value_group["count"] >= self.min_obs_thresh:
            return feature_value_group["value"]
        return None

    def get_name(self) -> str:
        return f"{self.__class__.__name__}_{self.window_size}_{self.min_obs_thresh}"


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
        if post_position != "-1" and race_card.distance > 0:
            momentum = get_momentum(race_card, horse)
            if momentum > 0:
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


class TrackVariantSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.is_first_pre_update = True

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.post_update(race_card)

    def pre_update(self, race_card: RaceCard) -> None:
        if self.is_first_pre_update:
            RaceCard.reset_track_variant_estimate()
            self.is_first_pre_update = False

        self.update_track_variant(race_card)

    def update_horse(self, race_card: RaceCard, horse: Horse):
        pass

    def post_update(self, race_card: RaceCard) -> None:
        self.is_first_pre_update = True
        if race_card.race_result is not None:
            self.update_par_momentum(race_card)

    def update_track_variant(self, race_card: RaceCard) -> None:
        par_momentum = race_card.get_par_momentum_estimate["avg"]
        for horse in race_card.horses:
            momentum = get_uncorrected_momentum(race_card, horse)

            if par_momentum and momentum > 0:
                track_variant = par_momentum / momentum
                self.update_average(
                    category=race_card.track_variant_estimate,
                    new_obs=track_variant,
                    new_obs_date=race_card.date,
                    online_calculator=SimpleOnlineCalculator(),
                )

    def update_par_momentum(self, race_card: RaceCard):
        for horse in race_card.horses:
            momentum = get_uncorrected_momentum(race_card, horse)

            if momentum > 0:
                self.update_average(
                    category=race_card.get_par_momentum_estimate,
                    new_obs=momentum,
                    new_obs_date=race_card.date,
                    online_calculator=PAR_MOMENTUM_CALCULATOR,
                )


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
