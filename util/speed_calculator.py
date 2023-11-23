from collections import deque
from enum import Enum

LENGTHS_PER_SECOND = 5
METERS_PER_LENGTH: float = 2.4
__speed_figures_distribution = deque(maxlen=1000)


def get_speed_figures_distribution() -> deque:
    return __speed_figures_distribution


def compute_speed_figure(
        race_id: str,
        base_time_mean: float,
        base_time_std: float,
        lengths_per_second: float,
        win_time: float,
        distance: float,
        horse_distance: float,
        track_variant: float,
) -> float:
    # if is_horse_distance_too_far_from_winner(distance, horse_distance):
    #     return None

    if horse_distance < 0 or win_time <= 0 or not base_time_mean or base_time_std == 0 or not track_variant:
        return None

    horse_time = get_horse_time(win_time, lengths_per_second, horse_distance)
    track_corrected_horse_time = (1 - track_variant) * horse_time

    speed_figure = (base_time_mean - track_corrected_horse_time) / base_time_std

    if speed_figure < -10:
        print("----------------------------------")
        print(f"race id: {race_id}")
        print(f"track variant: {track_variant}")
        print(f"speed figure: {speed_figure}")
        print(f"base time mean: {base_time_mean}")
        print(f"base time std: {base_time_std}")
        print(f"win time: {win_time}")
        print(f"horse time: {horse_time}")
        print(f"track_corrected_horse_time: {track_corrected_horse_time}")
        print(f"lengths per second: {lengths_per_second}")
        print("----------------------------------")

    return speed_figure


def get_velocity(win_time: float, lengths_per_second: float, horse_distance: float, race_distance: float):
    horse_time = get_horse_time(win_time, lengths_per_second, horse_distance)

    return race_distance / horse_time


def get_horse_time(win_time: float, lengths_per_second: float, horse_distance: float):
    seconds_behind_winner = ((1 / lengths_per_second) * horse_distance)

    return win_time + seconds_behind_winner


class Going(Enum):
    # Going Code: Lower leads to faster times, higher leads to slower times.
    SOLID = 2
    GOOD = 3
    SOFT = 4


class RaceType(Enum):

    FLAT = "G"
    JUMP = "J"


# TODO: Arab and Pony races should be same as jump category, NH races are separate category
def get_lengths_per_second(track_name: str, race_type: str, surface: str, going: float) -> float:
    # conversion according to:
    # https://www.britishhorseracing.com/wp-content/uploads/2014/04/Lengths-Per-Second-Scale-Tables-2019.pdf
    if race_type == RaceType.FLAT.value:
        if surface == "TRF":
            if going <= Going.GOOD.value:
                return 6
            if going >= Going.SOFT.value:
                return 5

            return 5.5

        if surface == "EQT":
            if track_name in ["Kempton", "Lingfield", "Wolverhampton", "Newcastle", "Chelmsford", "Chelmsford City"]:
                return 6
            if track_name in ["Southwell"]:
                return 5
            # TODO: Chelmsford and Chelmsford are in the data
            # print("length conversion failed:")
            # print(track_name)

    if race_type == RaceType.JUMP.value:
        if going <= Going.GOOD.value:
            return 5
        if going >= Going.SOFT.value:
            return 4
        return 4.5

    return 5.0


def is_horse_distance_too_far_from_winner(race_distance: float, horse_distance: float) -> bool:
    return ((horse_distance * METERS_PER_LENGTH) / race_distance) > 0.01


def race_card_track_to_win_time_track(track_name: str) -> str:
    if "Ascot" in track_name:
        return "Ascot"
    if "Epsom" in track_name:
        return "Epsom Downs"
    if track_name == "Bangor":
        return "Bangor-On-Dee"
    if track_name == "Chelmsford":
        return "Chelmsford City"
    if track_name == "Glorious Goodwood":
        return "Goodwood"
    if track_name == "Perth Hunt":
        return "Perth"
    if track_name == "Chelmsford PMU":
        return "Chelmsford City"
    if track_name == "Carlise PMU":
        return "Carlisle"
    if "PMU" in track_name:
        return track_name[:-4]
    return track_name
