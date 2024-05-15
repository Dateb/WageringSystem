import datetime

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Trainer import Trainer


def has_won(race_card: RaceCard, horse: Horse) -> float:
    return float(horse.has_won)


def has_placed(race_card: RaceCard, horse: Horse) -> float:
    return float(horse.has_placed)


def purse(race_card: RaceCard, horse: Horse) -> float:
    return horse.purse


def one_constant(race_card: RaceCard, horse: Horse) -> float:
    return 1.0


def win_probability(race_card: RaceCard, horse: Horse) -> float:
    win_prob = horse.sp_win_prob

    if win_prob > 0:
        return win_prob

    return None


def place_percentile(race_card: RaceCard, horse: Horse) -> float:
    return horse.place_percentile


def competitors_beaten(race_card: RaceCard, horse: Horse) -> float:
    return horse.competitors_beaten_probability


def relative_distance_behind(race_card: RaceCard, horse: Horse):
    return horse.relative_distance_behind


def has_pulled_up(race_card: RaceCard, horse: Horse) -> float:
    has_pulled_up = horse.result_finish_dnf == "PU"

    return float(has_pulled_up)


def race_distance(race_card: RaceCard, horse: Horse) -> float:
    race_distance = race_card.distance

    if race_distance > 0:
        return race_distance

    return None


def adjusted_race_distance(race_card: RaceCard, horse: Horse) -> float:
    if race_card.adjusted_distance > 0:
        return race_card.adjusted_distance

    if race_card.distance > 0:
        return race_card.distance

    return None


def race_class(race_card: RaceCard, horse: Horse) -> float:
    race_class = race_card.race_class

    if race_class not in ["A", "B", "C", "O"]:
        return int(race_class)

    return None


def weight(race_card: RaceCard, horse: Horse) -> float:
    weight = horse.jockey.weight

    if weight > 0:
        return weight

    return None


def race_date(race_card: RaceCard, horse: Horse) -> datetime.date:
    return race_card.date


def get_track_name(race_card: RaceCard, horse: Horse) -> str:
    return race_card.track_name


def get_trainer_id(race_card: RaceCard, horse: Horse) -> str:
    return horse.trainer.id


def get_trainer(race_card: RaceCard, horse: Horse) -> Trainer:
    return horse.trainer


def momentum(race_card: RaceCard, horse: Horse) -> float:
    return horse.momentum
