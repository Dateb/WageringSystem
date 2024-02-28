from abc import ABC, abstractmethod
from math import log


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

    def __init__(self, window_size: int = 8, fading_factor: float = 0.0):
        super().__init__()
        self.fading_factor = fading_factor
        self.window_size = window_size
        self.alpha = 2 / (window_size + 1)

    def calculate_average(self, old_average: float, new_obs: float, n_days_since_last_obs: int):
        average_fade_factor = 0
        if self.fading_factor > 0:
            average_fade_factor = self.fading_factor * log(self.fading_factor * n_days_since_last_obs) \
                if n_days_since_last_obs > (1 / self.fading_factor) else 0

        alpha = self.alpha + average_fade_factor

        return alpha * new_obs + (1 - alpha) * old_average

    def calculate_variance(self):
        pass
