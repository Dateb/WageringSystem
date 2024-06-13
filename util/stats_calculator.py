from abc import ABC, abstractmethod
from math import log
from typing import List

import numpy as np


class OnlineCalculator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def calculate_average(self, old_average: float, new_obs: float, n_days_since_last_obs: int):
        pass

    @abstractmethod
    def calculate_variance(self):
        pass


class SimpleOnlineCalculator(OnlineCalculator):

    def __init__(self):
        super().__init__()

    def calculate_average(self, old_average: float, new_obs: float, n_days_since_last_obs: int, count: int):
        return ((count - 1) * old_average + new_obs) / count

    def calculate_variance(self):
        pass


# class EMACalculator(OnlineCalculator):
#
#     def __init__(self, window_size: int):
#         super().__init__()
#         self.window_size = window_size
#         self.k = 2 / (self.window_size + 1)
#         self.obs_count = 0
#         self.current_average = 0
#
#     def calculate_average(self, new_obs: float) -> float:
#         self.obs_count += 1
#         if self.obs_count <= self.window_size:
#             self.current_average = ((self.obs_count - 1) * self.current_average + new_obs) / self.obs_count
#             return self.current_average
#
#         self.current_average = self.k * new_obs + (1 - self.k) * self.current_average
#         return self.current_average
#
#     def calculate_variance(self, old_variance: float, new_obs: float, count: int, avg: float) -> float:
#         pass


class ExponentialOnlineCalculator(OnlineCalculator):

    def __init__(self, window_size: float = 0.9):
        super().__init__()
        self.window_size = window_size
        self.alpha = 2 / (window_size + 1)

    def calculate_average(self, old_average: float, new_obs: float, n_days_since_last_obs: int) -> float:
        w_avg = np.exp(-self.window_size * (n_days_since_last_obs+1))
        w_new_obs = 1 - w_avg

        new_average = (w_avg * old_average + w_new_obs * new_obs) / (w_avg + w_new_obs)

        return new_average

    def calculate_variance(self):
        pass


def get_max_draw_down(values: List[float]) -> float:
    max_draw_down = 0
    peak = 0

    sum_payouts = np.cumsum(values)

    for sum_payout in sum_payouts:
        draw_down = peak - sum_payout
        if draw_down > max_draw_down:
            max_draw_down = draw_down

        if sum_payout > peak:
            peak = sum_payout

    return max_draw_down
