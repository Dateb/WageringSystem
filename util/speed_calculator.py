from collections import deque

BASE_SPEED_CATEGORY_LENGTHS_PER_SECOND = 6.77
__speed_figures_distribution = deque(maxlen=10000)


def get_speed_figures_distribution() -> deque:
    return __speed_figures_distribution


def compute_speed_figure(
        base_time_mean: float,
        base_time_std: float,
        length_modifier: float,
        base_length_modifier: float,
        win_time: float,
        horse_distance: float,
        track_variant: float,
) -> float:
    # TODO: just a quick and dirty mapping. The win times data should rename its track names after the ones on racebets.
    if horse_distance < 0 or win_time <= 0 or not base_time_mean or base_time_std == 0 or not track_variant:
        return None

    horse_time = get_horse_time(win_time, length_modifier, base_length_modifier, horse_distance)
    horse_time = (1 - track_variant) * horse_time

    speed_figure = (base_time_mean - horse_time) / base_time_std

    if speed_figure < -5:
        speed_figure = -5
    if speed_figure > 5:
        speed_figure = 5

    get_speed_figures_distribution().append(speed_figure)
    return speed_figure


def get_horse_time(win_time: float, length_modifier: float, base_length_modifier: float, horse_distance: float):
    seconds_behind_winner = ((1 / get_lengths_per_second(length_modifier, base_length_modifier)) * horse_distance)

    return win_time + seconds_behind_winner


def get_lengths_per_second(length_modifier: float, base_length_modifier: float) -> float:
    if not length_modifier or not base_length_modifier:
        return 5

    distance_modifier = length_modifier / base_length_modifier
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