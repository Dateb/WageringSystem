from collections import deque

from util.nested_dict import nested_dict

__base_times = nested_dict()
__speed = nested_dict()
__base_speed_category = __speed["Wolverhampton"]["1437"]["EQT"]["0"]["FLT"]
BASE_SPEED_CATEGORY_LENGTHS_PER_SECOND = 6.25
__speed_figures_distribution = deque(maxlen=10000)


def get_speed_figures_distribution() -> deque:
    return __speed_figures_distribution


def get_base_time(track_name: str, distance: str, track_surface: str, going: str, race_type_detail: str) -> dict:
    return __base_times[track_name][distance][track_surface][going][race_type_detail]


def get_speed(track_name: str, distance: str, track_surface: str, going: str, race_type_detail: str) -> dict:
    return __speed[track_name][distance][track_surface][going][race_type_detail]


def compute_speed_figure(
        date: str,
        track_name: str,
        distance: float,
        win_time: float,
        horse_distance: float,
        race_type: str,
        race_type_detail: str,
        surface: str,
        going: float,
) -> float:
    # TODO: just a quick and dirty mapping. The win times data should rename its track names after the ones on racebets.
    win_time_track = race_card_track_to_win_time_track(track_name)
    base_time = get_base_time(win_time_track, str(distance), surface, str(going), race_type_detail)
    time_avg = base_time["avg"]
    if horse_distance < 0 or distance <= 0 or win_time <= 0 or not isinstance(time_avg, float):
        return None

    horse_time = get_horse_time(win_time, win_time_track, str(distance), surface, str(going), race_type_detail, horse_distance)

    time_std = base_time["std"]

    if time_std == 0:
        horse_speed_figure = 0
    else:
        horse_speed_figure = (time_avg - horse_time) / time_std

    if horse_speed_figure < -3:
        horse_speed_figure = -3
    if horse_speed_figure > 3:
        horse_speed_figure = 3

    if horse_speed_figure < -300:
        print(date)
        print(distance)
        print(win_time)
        print(horse_distance)
        print("-------------------------")

    get_speed_figures_distribution().append(horse_speed_figure)
    return horse_speed_figure


def get_horse_time(win_time: float, track_name: str, distance: str, track_surface: str, going: str, race_type_detail: str, horse_distance: float):
    seconds_behind_winner = ((1 / get_lengths_per_second(track_name, distance, track_surface, going, race_type_detail)) * horse_distance)

    return win_time + seconds_behind_winner


def get_lengths_per_second(track_name: str, distance: str, track_surface: str, going: str, race_type_detail: str) -> float:
    if "avg" not in __base_speed_category:
        return 5
    base_speed = __base_speed_category["avg"]
    category_speed = get_speed(track_name, distance, track_surface, going, race_type_detail)["avg"]

    distance_modifier = category_speed / base_speed
    lengths_per_second = BASE_SPEED_CATEGORY_LENGTHS_PER_SECOND * distance_modifier
    return lengths_per_second


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

#gut-fest: 2.5
#gut: 3
#gut-weich: 3.5
#weich: 4