from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard


def win_probability(race_card: RaceCard, horse: Horse) -> float:
    return horse.betfair_win_sp


def momentum(race_card: RaceCard, horse: Horse) -> float:
    uncorrected_momentum = get_uncorrected_momentum(race_card, horse)
    if uncorrected_momentum > 0:
        track_variant = 1.0
        if "avg" in race_card.track_variant_estimate:
            track_variant = race_card.track_variant_estimate["avg"]

        return uncorrected_momentum * track_variant

    return -1


def get_uncorrected_momentum(race_card: RaceCard, horse: Horse) -> float:
    if horse.jockey.weight > 0:
        velocity = get_velocity(race_card, horse)
        if velocity > 0:
            return velocity * horse.jockey.weight

    return -1.0


def get_velocity(race_card: RaceCard, horse: Horse) -> float:
    if race_card.distance > 0:
        if horse.finish_time > 0:
            return race_card.distance / horse.finish_time

        if race_card.win_time > 0 and horse.horse_distance >= 0:
            horse_m_behind = horse_lengths_behind_to_horse_m_behind(horse.horse_distance)
            total_m_run = race_card.distance - horse_m_behind

            return total_m_run / race_card.win_time

    return -1


def horse_lengths_behind_to_horse_m_behind(horse_distance: float) -> float:
    metres_per_length = 2.4
    return horse_distance * metres_per_length
