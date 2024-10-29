import datetime

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Trainer import Trainer

class ValueCalculator:
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse):
        raise NotImplementedError("Subclasses should implement this method.")

    @property
    def name(self) -> str:
        return self.__class__.__name__

class HasWonCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return float(horse.has_won)

class HasPlacedCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return float(horse.has_placed)

class PurseCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.purse

class OneConstantCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return 1.0

class WinProbabilityCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.sp_win_prob

class RatingCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.rating

class PlacePercentileCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.place_percentile

class CompetitorsBeatenCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.competitors_beaten_probability

class RelativeDistanceBehindCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.relative_distance_behind

class HasPulledUpCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        has_pulled_up = horse.result_finish_dnf == "PU"
        return float(has_pulled_up)

class RaceDistanceCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.distance > 0:
            return race_card.distance
        return None

class AdjustedRaceDistanceCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.adjusted_distance > 0:
            return race_card.adjusted_distance
        if race_card.distance > 0:
            return race_card.distance
        return None

class RaceClassCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.race_class not in ["A", "B", "C", "O"]:
            return int(race_card.race_class)
        return None

class RaceGoingCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.going)

class NumDaysCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return (race_card.datetime - datetime.datetime(2000, 1, 1)).days

class WeightCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        weight = horse.jockey.weight
        if weight > 0:
            return weight
        return None

class RaceDateCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> datetime.date:
        return race_card.date

class TrackNameCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> str:
        return race_card.track_name

class TrainerIdCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> str:
        return horse.trainer.id

class TrainerCalculator(ValueCalculator):
    is_available_before_race: bool = True

    def calculate(self, race_card: RaceCard, horse: Horse) -> Trainer:
        return horse.trainer

class MomentumCalculator(ValueCalculator):
    is_available_before_race: bool = False

    def calculate(self, race_card: RaceCard, horse: Horse) -> float:
        return horse.momentum
