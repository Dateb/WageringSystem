from abc import abstractmethod, ABC
from sqlite3 import Date
from typing import List

import numpy as np

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.feature_sources.value_calculators import ValueCalculator
from util.nested_dict import nested_dict


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
                    self.update_statistic(feature_value_group_data, new_feature_value, race_card.date)

    def post_update(self, race_cards: List[RaceCard], feature_values: dict, current_date: Date) -> None:
        for feature_value_group_key in feature_values:
            new_feature_value = feature_values[feature_value_group_key]["avg"]
            if new_feature_value is not None:
                self.update_statistic(self.feature_values[feature_value_group_key], new_feature_value, current_date)

    def get_feature_value(self, race_card: RaceCard, horse: Horse, feature_value_group: FeatureValueGroup) -> float:
        race_card_key = feature_value_group.get_race_card_key(race_card)
        feature_value_group_key = feature_value_group.get_key(race_card_key, horse)
        feature_value_group = self.feature_values[feature_value_group_key]
        if "value" in feature_value_group:
            return feature_value_group["value"]
        return None

    @abstractmethod
    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__


class PreviousSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        category["value"] = new_feature_value


class DiffPreviousSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        prev_value = category.get("prev_value", None)
        category["value"] = None if prev_value is None else new_feature_value - prev_value
        category["prev_value"] = new_feature_value


class SimpleAverageSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        category["count"] = category.get("count", 0) + 1
        count = category["count"]

        old_avg = category.get("value", 0)
        category["value"] = ((count - 1) * old_avg + new_feature_value) / count

class DiffAverageSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        average_value = category.get("average_value", None)
        category["value"] = None if average_value is None else new_feature_value - average_value

        category["count"] = category.get("count", 0) + 1
        count = category["count"]

        old_avg = category.get("average_value", 0)
        category["average_value"] = ((count - 1) * old_avg + new_feature_value) / count

class EMASource(FeatureSource):

    def update_statistic(self, category: dict, new_obs: float, value_date: Date) -> None:
        decay_factor = 0.01
        old_avg = category.get("value", None)
        if old_avg is None:
            new_avg = new_obs
        else:
            new_avg = decay_factor * new_obs + (1.0 - decay_factor) * old_avg
        category["value"] = new_avg


class EMATimeSource(FeatureSource):

    def __init__(self, window_size: float):
        super().__init__()
        self.window_size = window_size

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        old_avg = category.get("value", None)
        if old_avg is None:
            new_avg = new_feature_value
        else:
            n_days_since_last_obs = (value_date - category["last_obs_date"]).days

            w_avg = np.exp(-self.window_size * (n_days_since_last_obs + 1))
            w_new_obs = 1 - w_avg

            new_avg = (w_avg * old_avg + w_new_obs * new_feature_value) / (w_avg + w_new_obs)

        category["last_obs_date"] = value_date
        category["value"] = new_avg

    def get_name(self) -> str:
        return f"{self.__class__.__name__}_{self.window_size}"


class StreakSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
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

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        if not category["value"] or new_feature_value > category["value"]:
            category["value"] = new_feature_value


class MinSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        if not category["value"] or new_feature_value < category["value"]:
            category["value"] = new_feature_value


class SumSource(FeatureSource):

    def update_statistic(self, category: dict, new_feature_value: float, value_date: Date) -> None:
        if not category["value"]:
            category["value"] = new_feature_value
        else:
            category["value"] += new_feature_value
