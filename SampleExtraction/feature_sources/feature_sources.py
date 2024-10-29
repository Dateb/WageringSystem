import collections
from abc import abstractmethod, ABC
from datetime import date
from sqlite3 import Date
from typing import List, Dict, Callable

from numpy import mean

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.feature_sources.value_calculators import ValueCalculator
from util.nested_dict import nested_dict
from util.stats_calculator import OnlineCalculator, ExponentialOnlineCalculator


class FeatureValueGroup:

    attributes: List[str]
    value_calculator: ValueCalculator

    def __init__(
            self,
            value_calculator: ValueCalculator,
            horse_attributes: List[str] = None,
            race_card_attributes: List[str] = None
    ):
        self.value_calculator = value_calculator

        self.horse_attributes = horse_attributes or []
        self.race_card_attributes = race_card_attributes or []

        self.race_card_key_cache = {}
        self.key_cache = {}

    def get_race_card_key(self, race_card: RaceCard) -> str:
        key = ""

        for attribute in self.race_card_attributes:
            attribute_key = race_card.__dict__[attribute]
            key += f"{attribute_key}_"

        self.race_card_key_cache[race_card.race_id] = key

        return key

    def get_key(self, race_card_key, horse: Horse) -> str:
        key = race_card_key

        for attribute in self.horse_attributes:
            attribute_key = horse.__dict__[attribute]
            key += f"{attribute_key}_"

        key += self.value_calculator.name

        self.key_cache[horse.subject_id] = key

        return key

    def clear_cache(self) -> None:
        self.race_card_key_cache = {}
        self.key_cache = {}

    @property
    def name(self) -> str:
        attribute_names = ""
        for attribute in self.horse_attributes:
            attribute_names += f"{attribute}_"
        for attribute in self.race_card_attributes:
            attribute_names += f"{attribute}_"
        return f"{attribute_names}{self.value_calculator.name}"


class FeatureSource(ABC):

    def __init__(self):
        self.feature_values = nested_dict()
        self.feature_value_groups: List[FeatureValueGroup] = []
        self.feature_value_group_names: List[str] = []

    def register_feature_value_group(self, feature_value_group: FeatureValueGroup):
        if feature_value_group.name not in self.feature_value_group_names:
            self.feature_value_groups.append(feature_value_group)
            self.feature_value_group_names.append(feature_value_group.name)

    def pre_update(self, race_card: RaceCard, horse: Horse):
        for feature_value_group in self.feature_value_groups:
            if feature_value_group.value_calculator.is_available_before_race:
                new_feature_value = feature_value_group.value_calculator.calculate(race_card, horse)
                if new_feature_value is not None:
                    race_card_key = feature_value_group.get_race_card_key(race_card)
                    feature_value_group_key = feature_value_group.get_key(race_card_key, horse)
                    feature_value_group_data = self.feature_values[feature_value_group_key]
                    self.update_statistic(feature_value_group_data, new_feature_value)

    def post_update(self, race_cards: List[RaceCard], feature_values: dict, current_date: Date) -> None:
        for feature_value_group_key in feature_values:
            new_feature_value = feature_values[feature_value_group_key]["avg"]
            if new_feature_value is not None:
                self.update_statistic(self.feature_values[feature_value_group_key], new_feature_value)

    def get_feature_value(self, race_card: RaceCard, horse: Horse, feature_value_group: FeatureValueGroup) -> float:
        race_card_key = feature_value_group.get_race_card_key(race_card)
        feature_value_group_key = feature_value_group.get_key(race_card_key, horse)
        feature_value_group = self.feature_values[feature_value_group_key]
        if "value" in feature_value_group:
            return feature_value_group["value"]
        return None

    @abstractmethod
    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__


class PreviousSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        category["value"] = new_feature_value


class DiffPreviousSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        prev_value = category.get("prev_value", None)
        category["value"] = None if prev_value is None else new_feature_value - prev_value
        category["prev_value"] = new_feature_value


class SimpleAverageSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        category["count"] = category.get("count", 0) + 1
        count = category["count"]

        old_avg = category.get("value", 0)
        category["value"] = ((count - 1) * old_avg + new_feature_value) / count

class DiffAverageSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        average_value = category.get("average_value", None)
        category["value"] = None if average_value is None else new_feature_value - average_value

        category["count"] = category.get("count", 0) + 1
        count = category["count"]

        old_avg = category.get("average_value", 0)
        category["average_value"] = ((count - 1) * old_avg + new_feature_value) / count

class EMASource(FeatureSource):

    def update_statistic(self, category: dict, new_obs: float) -> None:
        decay_factor = 0.01
        old_avg = category.get("value", None)
        if old_avg is None:
            new_avg = new_obs
        else:
            new_avg = decay_factor * new_obs + (1.0 - decay_factor) * old_avg
        category["value"] = new_avg


class StreakSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        if new_feature_value == 1:
            if "value" not in category or category["value"] < 0:
                category["value"] = 1
            else:
                category["value"] += 1

        if new_feature_value == 0:
            if "value" not in category or category["value"] > 0:
                category["value"] = -1
            else:
                category["value"] -= 1


class MaxSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        if not category["value"] or new_feature_value > category["value"]:
            category["value"] = new_feature_value


class MinSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        if not category["value"] or new_feature_value < category["value"]:
            category["value"] = new_feature_value


class SumSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        if not category["value"]:
            category["value"] = new_feature_value
        else:
            category["value"] += new_feature_value


class CountSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
        if not category["value"]:
            category["value"] = 1
        else:
            category["value"] += 1


class NonRunnerReasonDateSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float) -> None:
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


class TrackVariantSource(SimpleAverageSource):

    def __init__(self):
        super().__init__()
        self.is_first_pre_update = True
        self.track_variant_average_calculator = ExponentialOnlineCalculator(window_size=0.01)
        self.par_momentum_average_calculator = ExponentialOnlineCalculator(window_size=0.01)

    def pre_update(self, race_card: RaceCard) -> None:
        if race_card.has_results:
            if self.is_first_pre_update:
                RaceCard.reset_track_variant_estimate()
                self.is_first_pre_update = False

            self.update_track_variant(race_card)

    def update_horse(self, race_card: RaceCard, horse: Horse) -> None:
        pass

    def post_update(self, race_cards: List[RaceCard], feature_values: dict, current_date: Date) -> None:
        self.is_first_pre_update = True
        for race_card in race_cards:
            if race_card.race_result is not None:
                self.update_par_momentum(race_card)

    def update_track_variant(self, race_card: RaceCard) -> None:
        par_momentum = race_card.get_par_momentum_estimate["value"]
        track_variants = [par_momentum / horse.uncorrected_momentum for horse in race_card.horses
                          if horse.uncorrected_momentum > 0 and par_momentum]
        if track_variants:
            mean_track_variant = mean(track_variants)
            self.update_statistic(
                category=race_card.track_variant_estimate,
                new_feature_value=mean_track_variant,
                value_date=race_card.date,
                average_calculator=self.track_variant_average_calculator
            )

    def update_par_momentum(self, race_card: RaceCard) -> None:
        momentums = [horse.uncorrected_momentum for horse in race_card.horses if horse.uncorrected_momentum > 0]
        if momentums:
            mean_momentum = mean(momentums)
            self.update_statistic(
                category=race_card.get_par_momentum_estimate,
                new_feature_value=mean_momentum,
                value_date=race_card.date,
                average_calculator=self.par_momentum_average_calculator
            )


class GoingSource(SimpleAverageSource):

    def __init__(self):
        super().__init__()
        self.goings = {}

    def pre_update(self, race_card: RaceCard) -> None:
        if race_card.track_name in self.goings:
            race_card.estimated_going = self.goings[race_card.track_name]

    def update_horse(self, race_card: RaceCard, horse: Horse) -> None:
        pass

    def post_update(self, race_cards: List[RaceCard], feature_values: dict, current_date: Date) -> None:
        for race_card in race_cards:
            self.goings[race_card.track_name] = race_card.going


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
