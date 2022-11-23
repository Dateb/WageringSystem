from math import sqrt

from Persistence.JSONPersistence import JSONPersistence
from util.nested_dict import nested_dict

__base_times = nested_dict()
__win_times = JSONPersistence("win_times_contextualized").load()

LOWER_KM_PER_HOUR_LIMIT = 35
UPPER_KM_PER_HOUR_LIMIT = 50


def get_base_time(track_name: str, distance: str, race_type_detail: str) -> dict:
    return __base_times[track_name][distance][race_type_detail]


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
    win_times_track_name = race_card_track_to_win_time_track(track_name)
    base_time = __base_times[win_times_track_name][str(distance)][race_type_detail]["avg"]
    if horse_distance < 0 or distance <= 0 or win_time <= 0 or not isinstance(base_time, float):
        return None

    if str(distance) not in __base_times[win_times_track_name]:
        return None

    if not win_time_feasible(win_time, distance):
        return None

    horse_time = get_horse_time(win_time, win_times_track_name, race_type, surface, going, horse_distance)

    time_avg = __base_times[win_times_track_name][str(distance)][race_type_detail]["avg"]
    time_std = __base_times[win_times_track_name][str(distance)][race_type_detail]["std"]

    if time_std == 0:
        horse_speed_figure = 0
    else:
        horse_speed_figure = (time_avg - horse_time) / time_std

    if horse_speed_figure < -300:
        print(date)
        print(track_name)
        print(distance)
        print(win_time)
        print(horse_distance)
        print("-------------------------")

    return horse_speed_figure


def win_time_feasible(win_time, distance) -> bool:
    distance_km = distance / 1000
    km_per_second = distance_km / win_time
    km_per_hour = km_per_second * 3600
    if LOWER_KM_PER_HOUR_LIMIT < km_per_hour < UPPER_KM_PER_HOUR_LIMIT:
        return True
    return False


def get_horse_time(win_time: float, track_name: str, race_type: str, surface: str, going: float, horse_distance: float):
    seconds_behind_winner = ((1 / get_lengths_per_second(track_name, race_type, surface, going)) * horse_distance)

    return win_time + seconds_behind_winner


def get_lengths_per_second(track_name: str, race_type: str, surface: str, going: float) -> float:
    if race_type == "G":
        if surface == "TRF":
            if going <= 3:
                return 6
            if going >= 4:
                return 5
        if surface == "EQT":
            if track_name in ["Kempton", "Lingfield", "Wolverhampton", "Newcastle", "Chelmsford", "Chelmsford City"]:
                return 6
            if track_name in ["Southwell"]:
                return 5
            # TODO: Chelmsford and Chelmsford are in the data
            print("length conversion failed:")
            print(track_name)
    if race_type == "J":
        if going <= 3:
            return 5
        if going >= 4:
            return 4
        return 4.5

    return 5.0


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