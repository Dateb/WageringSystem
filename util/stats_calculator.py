from abc import ABC, abstractmethod
from math import log


class OnlineCalculator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def calculate_average(self, old_average: float, new_obs: float, count: int, n_days_since_last_obs: int):
        pass

    @abstractmethod
    def calculate_variance(self):
        pass


class SimpleOnlineCalculator(OnlineCalculator):

    def __init__(self):
        super().__init__()

    def calculate_average(self, old_average: float, new_obs: float, count: int, n_days_since_last_obs: int):
        return ((count - 1) * old_average + new_obs) / count

    def calculate_variance(self):
        pass


class ExponentialOnlineCalculator(OnlineCalculator):

    def __init__(self, base_alpha: float = 0.125, fading_factor: float = 0.0):
        super().__init__()
        self.fading_factor = fading_factor
        self.base_alpha = base_alpha

    def calculate_average(self, old_average: float, new_obs: float, count: int, n_days_since_last_obs: int):
        average_fade_factor = 0
        if self.fading_factor > 0:
            average_fade_factor = self.fading_factor * log(self.fading_factor * n_days_since_last_obs) \
                if n_days_since_last_obs > (1 / self.fading_factor) else 0

        alpha = self.base_alpha + average_fade_factor

        return alpha * new_obs + (1 - alpha) * old_average

    def calculate_variance(self):
        pass
