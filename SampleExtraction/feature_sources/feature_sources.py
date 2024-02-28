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
from SampleExtraction.feature_sources.value_calculators import get_uncorrected_momentum
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, ExponentialOnlineCalculator

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
        attribute_names = ""
        for attribute in self.attributes:
            attribute_names += f"{attribute}_"
        return f"{attribute_names}{self.value_name}"


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

    def get_name(self) -> str:
        return self.__class__.__name__


class PreviousValueSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if new_feature_value is not None:
            category["value"] = new_feature_value


class PreviousValueScratchedSource(PreviousValueSource):

    def post_update(self, race_card: RaceCard):
        for horse in race_card.horses:
            if horse.is_scratched:
                self.update_horse(race_card, horse)


class MaxValueSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if new_feature_value is not None and (not category["value"] or new_feature_value > category["value"]):
            category["value"] = new_feature_value


class MinValueSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if new_feature_value is not None and (not category["value"] or new_feature_value < category["value"]):
            category["value"] = new_feature_value


class SumSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if not category["value"]:
            category["value"] = new_feature_value
        else:
            category["value"] += new_feature_value


class CountSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if not category["value"]:
            category["value"] = 1
        else:
            category["value"] += 1


class AverageValueSource(FeatureSource):

    def __init__(self, window_size=5, min_obs_thresh=3):
        super().__init__()
        self.window_size = window_size
        self.track_variant_average_calculator = ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.0)
        self.min_obs_thresh = min_obs_thresh

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date, average_calculator: OnlineCalculator=None) -> None:
        if new_feature_value is not None:
            if "prev_avg" not in category:
                category["prev_avg"] = 0
                category["value"] = new_feature_value
                category["last_obs_date"] = value_date
            else:
                if new_feature_value == -1:
                    print(f'yellow. new feature value == -1. cat: {category}')
                n_days_since_last_obs = (value_date - category["last_obs_date"]).days

                category["prev_avg"] = category["value"]

                if average_calculator is None:
                    average_calculator = self.track_variant_average_calculator

                category["value"] = average_calculator.calculate_average(
                    old_average=category["prev_avg"],
                    new_obs=new_feature_value,
                    n_days_since_last_obs=n_days_since_last_obs,
                )
                category["last_obs_date"] = value_date

    def get_feature_value(self, race_card: RaceCard, horse: Horse, feature_value_group: FeatureValueGroup) -> float:
        feature_value_group_key = feature_value_group.get_key(race_card, horse)
        feature_value_group = self.feature_values[feature_value_group_key]
        if "value" in feature_value_group:
            return feature_value_group["value"]
        return None

    def get_name(self) -> str:
        return f"{self.__class__.__name__}_{self.window_size}_{self.min_obs_thresh}"


class NonRunnerReasonDateSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: date) -> None:
        if not category["value"]:
            category["value"] = 1
        else:
            category["value"] += 1


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


# class DrawBiasSource(FeatureSource):
#
#     def __init__(self):
#         super().__init__()
#         self.draw_bias = nested_dict()
#
#     def update_horse(self, race_card: RaceCard, horse: Horse):
#         track_name = race_card_track_to_win_time_track(race_card.track_name)
#         post_position = str(horse.post_position)
#         if post_position != "-1" and race_card.distance > 0:
#             momentum = get_momentum(race_card, horse)
#             if momentum > 0:
#                 self.update_average(
#                     self.draw_bias[track_name][post_position],
#                     momentum,
#                     race_card.date,
#                     DRAW_BIAS_CALCULATOR,
#                 )
#
#     def get_draw_bias(self, track_name: str, post_position: int):
#         if track_name not in self.draw_bias or str(post_position) not in self.draw_bias[track_name]:
#             return -1
#         return self.draw_bias[track_name][str(post_position)]["avg"]


class TrackVariantSource(AverageValueSource):

    def __init__(self):
        super().__init__()
        self.is_first_pre_update = True
        self.track_variant_average_calculator = ExponentialOnlineCalculator()
        self.par_momentum_average_calculator = ExponentialOnlineCalculator()

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
        par_momentum = race_card.get_par_momentum_estimate["value"]
        for horse in race_card.horses:
            momentum = get_uncorrected_momentum(race_card, horse)

            if par_momentum and momentum > 0:
                track_variant = par_momentum / momentum
                self.update_statistic(
                    category=race_card.track_variant_estimate,
                    new_feature_value=track_variant,
                    value_date=race_card.date,
                    average_calculator=self.track_variant_average_calculator
                )

    def update_par_momentum(self, race_card: RaceCard):
        for horse in race_card.horses:
            momentum = get_uncorrected_momentum(race_card, horse)

            if momentum > 0:
                self.update_statistic(
                    category=race_card.get_par_momentum_estimate,
                    new_feature_value=momentum,
                    value_date=race_card.date,
                    average_calculator=self.par_momentum_average_calculator
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
