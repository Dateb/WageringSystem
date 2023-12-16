from abc import ABC
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.feature_sources.feature_sources import FeatureSource, CATEGORY_AVERAGE_CALCULATOR
from util.nested_dict import nested_dict
from util.speed_calculator import get_lengths_per_second, get_velocity, get_momentum
from util.stats_calculator import ExponentialOnlineCalculator, OnlineCalculator


class CategoryAverageSource(FeatureSource, ABC):
    def __init__(self, average_calculator: OnlineCalculator = CATEGORY_AVERAGE_CALCULATOR):
        super().__init__()
        self.averages = nested_dict()
        self.average_attribute_groups = []
        self.average_calculator = average_calculator

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
                self.average_calculator,
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

    def get_average_of_name(self, name: str) -> float:
        average_elem = self.averages[name]

        if "avg" in average_elem:
            return average_elem["avg"]

        return -1

    def get_count_of_name(self, name: str) -> int:
        average_elem = self.averages[name]

        if "avg" in average_elem:
            return average_elem["count"]

        return 0


class AverageRelativeDistanceBehindSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))
        self.average_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.horse_distance >= 0 and race_card.distance > 0:
            if horse.place == 1:
                second_place_horse = race_card.get_horse_by_place(2)
                second_place_distance = 0
                if second_place_horse is not None:
                    second_place_distance = second_place_horse.horse_distance

                relative_distance_ahead = second_place_distance / race_card.distance
                self.insert_value_into_avg(race_card, horse, relative_distance_ahead)
            else:
                relative_distance_behind = -(horse.horse_distance / race_card.distance)
                self.insert_value_into_avg(race_card, horse, relative_distance_behind)


class AverageWinProbabilitySource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.sp_win_prob > 0:
            self.insert_value_into_avg(race_card, horse, horse.sp_win_prob)


class WinRateSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, horse.has_won)


class ShowRateSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        show_indicator = int(1 <= horse.place <= race_card.places_num)
        self.insert_value_into_avg(race_card, horse, show_indicator)


class AveragePlacePercentileSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.place > 0 and len(race_card.runners) > 1:
            place_percentile = (horse.place - 1) / (len(race_card.runners) - 1)
            self.insert_value_into_avg(race_card, horse, place_percentile)


class AverageVelocitySource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if race_card.distance > 0:
            velocity = get_velocity(race_card.win_time, horse.horse_distance, horse.finish_time, race_card.distance)
            if velocity > 0:
                self.insert_value_into_avg(race_card, horse, velocity)


class AverageMomentumSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        momentum = get_momentum(race_card, horse)
        if momentum > 0:
            self.insert_value_into_avg(race_card, horse, momentum)


class AverageJockeyWeightSource(CategoryAverageSource):

    def __init__(self, window_size=5):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=window_size, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.jockey.weight > 0:
            self.insert_value_into_avg(race_card, horse, horse.jockey.weight)


class ScratchedHorseCategoryAverageSource(CategoryAverageSource, ABC):

    def __init__(self):
        super().__init__()

    def post_update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.update_horse(race_card, horse)


class PurseRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__(average_calculator=ExponentialOnlineCalculator(window_size=8, fading_factor=0.1))

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, horse.purse)


class PulledUpRateSource(CategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, horse.pulled_up)


class ScratchedRateSource(ScratchedHorseCategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, int(horse.is_scratched))