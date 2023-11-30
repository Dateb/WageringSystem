from abc import ABC
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.Jockey import Jockey
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.feature_sources.feature_sources import FeatureSource
from util.nested_dict import nested_dict
from util.speed_calculator import get_velocity, LENGTHS_PER_SECOND, get_lengths_per_second


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


class PreviousJockeySource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.jockey)


class PreviousOwnerSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.owner)


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
        if horse.sp_win_prob == 0:
            print(f"yellow: {race_card.race_id}")
        self.insert_previous_value(race_card, horse, horse.sp_win_prob)


class PreviousDistanceSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, race_card.distance)


class PreviousVelocitySource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if race_card.win_time > 0 and horse.horse_distance >= 0 and race_card.distance > 0:
            velocity = get_velocity(race_card.win_time, horse.horse_distance, race_card.distance)
            self.insert_previous_value(race_card, horse, velocity)


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


class PreviousPulledUpSource(PreviousValueSource):

    def __init__(self):
        super().__init__()

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.pulled_up)


class PreviousTrainerSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        self.insert_previous_value(race_card, horse, horse.trainer)


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


class BestClassPlaceSource(PreviousValueSource):

    def __init__(self):
        super().__init__()
        self.previous_value_attribute_groups.append(["subject_id"])

    def update_horse(self, race_card: RaceCard, horse: Horse):
        if 1 <= horse.place <= 3 and race_card.race_class not in ["A", "B"]:
            best_class = self.get_previous_of_name(str(horse.subject_id))

            race_class_num = int(race_card.race_class)

            if best_class is None or race_class_num < best_class:
                self.insert_previous_value(race_card, horse, race_class_num)