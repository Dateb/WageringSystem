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


class ScratchedHorseCategoryAverageSource(CategoryAverageSource, ABC):

    def __init__(self):
        super().__init__()

    def post_update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.update_horse(race_card, horse)


class PreviousValueSource(FeatureSource, ABC):
    def __init__(self):
        super().__init__()
        self.previous_values = nested_dict()
        self.previous_value_attribute_groups = []

    def insert_previous_value(self, race_card: RaceCard, horse: Horse, value):
        for attribute_group in self.previous_value_attribute_groups:
            attribute_group_key = self.get_attribute_group_key(race_card, horse, attribute_group)

            self.update_previous(
                self.previous_values[attribute_group_key],
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

    def delete_previous_values(self, race_card: RaceCard, horse: Horse) -> None:
        self.previous_values[str(horse.subject_id)] = nested_dict()

    def get_previous_of_name(self, name: str) -> float:
        previous_elem = self.previous_values[name]
        if "previous" in previous_elem:
            return previous_elem["previous"]
        return None


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


class EquipmentAlreadyWornSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        already_worn_equipments = self.get_previous_of_name(str(horse.subject_id))

        self.insert_previous_value(race_card, horse, horse.equipments.union(already_worn_equipments))

    def get_previous_of_name(self, name: str):
        previous_elem = self.previous_values[name]
        if "previous" in previous_elem:
            return previous_elem["previous"]
        return set()


class MaxWinProbabilitySource(MaxValueSource):

    def __init__(self):
        super().__init__()
        self.max_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value(race_card, horse, horse.sp_win_prob)


class LifeTimeStartCountSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        start_count = self.get_previous_of_name(str(horse.subject_id))

        if start_count is None:
            start_count = 0

        self.insert_previous_value(race_card, horse, start_count + 1)


class LifeTimeWinCountSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        win_count = self.get_previous_of_name(str(horse.subject_id))

        if win_count is None:
            win_count = 0

        if horse.place == 1:
            self.insert_previous_value(race_card, horse, win_count + 1)


class LifeTimePlaceCountSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        place_count = self.get_previous_of_name(str(horse.subject_id))

        if place_count is None:
            place_count = 0

        if 1 <= horse.place <= race_card.places_num:
            self.insert_previous_value(race_card, horse, place_count + 1)


class PreviousPlacePercentileSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.place > 0 and len(race_card.runners) > 1:
            previous_place_percentile = (horse.place - 1) / (len(race_card.runners) - 1)
            self.insert_previous_value(race_card, horse, previous_place_percentile)
        else:
            # self.delete_previous_values(race_card, horse)
            self.insert_previous_value(race_card, horse, 1)


class PreviousRelativeDistanceBehindSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.horse_distance >= 0 and race_card.distance > 0:
            if horse.place == 1:
                second_place_horse = race_card.get_horse_by_place(2)
                second_place_distance = 0
                if second_place_horse is not None:
                    second_place_distance = second_place_horse.horse_distance

                relative_distance_ahead = second_place_distance / race_card.distance
                self.insert_previous_value(race_card, horse, relative_distance_ahead)
            else:
                relative_distance_behind = -(horse.horse_distance / race_card.distance)
                self.insert_previous_value(race_card, horse, relative_distance_behind)
        else:
            # self.delete_previous_values(race_card, horse)
            self.insert_previous_value(race_card, horse, -1)


class PreviousWinProbSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.sp_win_prob)


class PreviousWeightSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if horse.jockey.weight > 0:
            self.insert_previous_value(race_card, horse, horse.jockey.weight)


class PreviousDistanceSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.distance)


class PreviousRaceGoingSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.going)


class PreviousRaceClassSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.race_class)


class PreviousTrainerSource(PreviousValueSource):
    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.trainer_name)


class PreviousDateSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.datetime)

class PreviousTrackNameSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.track_name)


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


class ScratchedRateSource(ScratchedHorseCategoryAverageSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_value_into_avg(race_card, horse, int(horse.is_scratched))


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
        if post_position != "-1" and horse.horse_distance > 0 and race_card.distance > 0:
            self.update_average(
                self.draw_bias[track_name][post_position],
                horse.horse_distance / race_card.distance,
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


horse_name_to_subject_id_source: HorseNameToSubjectIdSource = HorseNameToSubjectIdSource()

# Average based sources:
win_rate_source: WinRateSource = WinRateSource()
show_rate_source: ShowRateSource = ShowRateSource()
purse_rate_source: PurseRateSource = PurseRateSource()
percentage_beaten_source: PercentageBeatenSource = PercentageBeatenSource()
scratched_rate_source: ScratchedRateSource = ScratchedRateSource()

life_time_start_count_source: LifeTimeStartCountSource = LifeTimeStartCountSource()
life_time_win_count_source: LifeTimeWinCountSource = LifeTimeWinCountSource()
life_time_place_count_source: LifeTimePlaceCountSource = LifeTimePlaceCountSource()

#Max based sources:
max_win_prob_source: MaxWinProbabilitySource = MaxWinProbabilitySource()

#Previous value based sources:
previous_win_prob_source: PreviousWinProbSource = PreviousWinProbSource()
previous_place_percentile_source: PreviousPlacePercentileSource = PreviousPlacePercentileSource()
previous_relative_distance_behind_source: PreviousRelativeDistanceBehindSource = PreviousRelativeDistanceBehindSource()
previous_track_name_source: PreviousTrackNameSource = PreviousTrackNameSource()

previous_weight_source: PreviousWeightSource = PreviousWeightSource()
previous_distance_source: PreviousDistanceSource = PreviousDistanceSource()
previous_race_going_source: PreviousRaceGoingSource = PreviousRaceGoingSource()
previous_race_class_source: PreviousRaceClassSource = PreviousRaceClassSource()

equipment_already_worn_source: EquipmentAlreadyWornSource = EquipmentAlreadyWornSource()

previous_trainer_source: PreviousTrainerSource = PreviousTrainerSource()

previous_date_source: PreviousDateSource = PreviousDateSource()

speed_figures_source: SpeedFiguresSource = SpeedFiguresSource()

draw_bias_source: DrawBiasSource = DrawBiasSource()

has_fallen_source: HasFallenSource = HasFallenSource()


def get_feature_sources() -> List[FeatureSource]:
    return [
        horse_name_to_subject_id_source,

        win_rate_source, show_rate_source, purse_rate_source, percentage_beaten_source, scratched_rate_source,

        life_time_start_count_source, life_time_win_count_source, life_time_place_count_source,

        max_win_prob_source,

        previous_win_prob_source,
        previous_place_percentile_source, previous_relative_distance_behind_source,
        previous_weight_source,

        previous_distance_source, previous_race_going_source, previous_race_class_source,
        previous_trainer_source,

        previous_date_source,
        previous_track_name_source,

        equipment_already_worn_source,

        draw_bias_source,

        # speed_figures_source,
        # has_fallen_source,
    ]
