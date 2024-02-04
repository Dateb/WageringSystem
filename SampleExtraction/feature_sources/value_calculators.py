import datetime

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Trainer import Trainer


def win_probability(race_card: RaceCard, horse: Horse) -> float:
    win_prob = horse.sp_win_prob

    if win_prob > 0:
        return win_prob

    return None


def place_percentile(race_card: RaceCard, horse: Horse) -> float:
    if horse.place > race_card.n_finishers:
        print(f"{horse.place}/{race_card.n_finishers}/{race_card.race_id}/{horse.name}")
        return None

    if horse.place > 0 and len(race_card.runners) > 1:
        if race_card.n_finishers == 1:
            return 1.0

        place_percentile = (horse.place - 1) / (race_card.n_finishers - 1)

        return 1 - place_percentile

    return None


def relative_distance_behind(race_card: RaceCard, horse: Horse):
    if horse.horse_distance >= 0 and race_card.adjusted_distance > 0:
        if horse.place_racebets == 1:
            second_place_horse = race_card.get_horse_by_place(2)
            second_place_distance = 0
            if second_place_horse is not None:
                second_place_distance = second_place_horse.horse_distance

            relative_distance_ahead = second_place_distance / race_card.adjusted_distance
            return relative_distance_ahead
        else:
            relative_distance_behind = -(horse.horse_distance / race_card.adjusted_distance)
            return relative_distance_behind

    return None


def has_pulled_up(race_card: RaceCard, horse: Horse) -> int:
    has_pulled_up = horse.result_finish_dnf == "PU"

    return has_pulled_up


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


def race_going(race_card: RaceCard, horse: Horse) -> float:
    race_going = race_card.going

    if race_going > 0:
        return race_going

    return None


def race_class(race_card: RaceCard, horse: Horse) -> float:
    race_class = race_card.race_class

    if race_class not in ["A", "B"]:
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
    uncorrected_momentum = get_uncorrected_momentum(race_card, horse)
    if uncorrected_momentum > 0:
        track_variant = 1.0
        if "value" in race_card.track_variant_estimate:
            track_variant = race_card.track_variant_estimate["value"]

        return uncorrected_momentum * track_variant

    return None


def get_uncorrected_momentum(race_card: RaceCard, horse: Horse) -> float:
    if horse.jockey.weight > 0:
        velocity = get_velocity(race_card, horse)
        if velocity > 0:
            return velocity * horse.jockey.weight

    return -1.0


def get_velocity(race_card: RaceCard, horse: Horse) -> float:
    if race_card.adjusted_distance > 0:
        if horse.finish_time > 0:
            return race_card.adjusted_distance / horse.finish_time

        if race_card.win_time > 0 and horse.horse_distance >= 0:
            horse_m_behind = horse_lengths_behind_to_horse_m_behind(horse.horse_distance)
            total_m_run = race_card.adjusted_distance - horse_m_behind

            return total_m_run / race_card.win_time

    return -1


def horse_lengths_behind_to_horse_m_behind(horse_distance: float) -> float:
    metres_per_length = 2.4
    return horse_distance * metres_per_length
