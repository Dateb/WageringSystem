from util.stats_calculator import SimpleOnlineCalculator

METERS_PER_LENGTH = 2.4


class BaseLengthEstimator:

    average_calculator = SimpleOnlineCalculator()

    def __init__(self):
        pass

    @staticmethod
    def update_lengths_per_second(category: dict, distance: float, win_time: float) -> None:
        meters_per_second = distance / win_time
        lengths_per_second = meters_per_second / METERS_PER_LENGTH

        if "base_avg" not in category:
            category["base_avg"] = lengths_per_second
            category["base_count"] = 1
        else:
            new_avg = BaseLengthEstimator.average_calculator.calculate_average(
                old_average=category["base_avg"],
                new_obs=lengths_per_second,
                count=category["base_count"],
                n_days_since_last_obs=0,
            )

            category["base_avg"] = new_avg
            category["base_count"] += 1
