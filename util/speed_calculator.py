from collections import deque

METERS_PER_LENGTH: float = 2.4
__speed_figures_distribution = deque(maxlen=1000)


def get_speed_figures_distribution() -> deque:
    return __speed_figures_distribution


def compute_speed_figure(
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

    speed_figure_base_shift = 20

    if horse_distance < 0 or win_time <= 0 or not base_time_mean or base_time_std == 0 or not track_variant:
        return None

    horse_time = get_horse_time(win_time, lengths_per_second, horse_distance)
    horse_time = (1 - track_variant) * horse_time

    speed_figure = (base_time_mean - horse_time) / base_time_std

    speed_figure = max([speed_figure, -speed_figure_base_shift + 1])

    return speed_figure + speed_figure_base_shift


def get_horse_time(win_time: float, lengths_per_second: float, horse_distance: float):
    if not lengths_per_second:
        lengths_per_second = 5

    seconds_behind_winner = ((1 / lengths_per_second) * horse_distance)

    return win_time + seconds_behind_winner


def get_lengths_per_second(distance: float, win_time: float) -> float:
    meters_per_second = distance / win_time
    lengths_per_second = meters_per_second / METERS_PER_LENGTH

    return lengths_per_second


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

#gut-fest: 2.5
#gut: 3
#gut-weich: 3.5
#weich: 4