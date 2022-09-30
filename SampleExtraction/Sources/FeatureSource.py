from abc import abstractmethod
from math import log
from sqlite3 import Date
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard


class FeatureSource:

    def __init__(self):
        self.base_alpha = 0.125

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float, new_obs_date: Date) -> None:
        if "avg" not in category:
            category["avg"] = new_obs
            category["count"] = 1
            category["last_obs_date"] = new_obs_date
        else:
            n_days_since_last_obs = (new_obs_date - category["last_obs_date"]).days
            average_fade_factor = 0.1 * log(0.1 * n_days_since_last_obs) if n_days_since_last_obs > 10 else 0

            alpha = self.base_alpha + average_fade_factor

            category["avg"] = alpha * new_obs + (1 - alpha) * category["avg"]
            category["count"] += 1
            category["last_obs_date"] = new_obs_date


__feature_container: FeatureSource = FeatureSource()


def get_feature_source() -> FeatureSource:
    return __feature_container
