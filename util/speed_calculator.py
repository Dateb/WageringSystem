from Persistence.JSONPersistence import JSONPersistence
from util.nested_dict import nested_dict

__base_times = nested_dict()
__win_times = JSONPersistence("win_times_contextualized").load()


def get_base_time(track_name: str, distance: str, race_class: str) -> dict:
    return __base_times[track_name][distance][race_class]


def compute_speed_figure(
        date: str,
        track_name: str,
        distance: str,
        race_class: str,
        win_time: float,
        horse_distance: float,
        race_type: str,
        surface: str,
        going: float,
) -> float:
    # TODO: just a quick and dirty mapping. The win times data should rename its track names after the ones on racebets.
    track_name = race_card_track_to_win_time_track(track_name)
    base_time = __base_times[track_name][distance][race_class]["avg"]
    if horse_distance == -1 or distance == -1 or not isinstance(base_time, float):
        return None

    if distance not in __base_times[track_name]:
        return None

    horse_time = get_horse_time(win_time, track_name, race_type, surface, going, horse_distance)
    track_variant = get_track_variant_time(date, distance, race_class, track_name)
    seconds_difference = (1 - track_variant) * (base_time - horse_time)

    points_per_second = __base_times[track_name][distance][race_class]["points per second"]

    horse_speed_figure = seconds_difference * points_per_second

    return horse_speed_figure


def get_horse_time(win_time: float, track_name: str, race_type: str, surface: str, going: float, horse_distance: float):
    seconds_behind_winner = ((1 / get_lengths_per_second(track_name, race_type, surface, going)) * horse_distance)

    return win_time + seconds_behind_winner


def get_track_variant_time(date: str, distance: str, race_class: str, track_name: str):
    track_time_biases = []

    for race in __win_times[date][track_name]:
        win_time = __win_times[date][track_name][race]["win_time"]
        base_time = __base_times[track_name][distance][race_class]["avg"]

        if win_time > 0 and isinstance(base_time, float):
            track_time_biases.append((win_time - base_time) / base_time)

    if track_time_biases:
        return sum(track_time_biases) / len(track_time_biases)
    else:
        return 0


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