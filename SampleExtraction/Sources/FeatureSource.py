from abc import abstractmethod
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard


class FeatureSource:

    def __init__(self):
        pass

    @abstractmethod
    def fit(self, race_cards: List[RaceCard]):
        pass

    def update_average(self, category: dict, new_obs: float) -> None:
        if "count" not in category:
            category["count"] = 1
            category["avg"] = new_obs
        else:
            category["count"] += 1
            new_count = category["count"]
            old_avg = category["avg"]

            new_avg = old_avg + (new_obs - old_avg) / new_count
            category["avg"] = new_avg


__feature_container: FeatureSource = FeatureSource()


def get_feature_source() -> FeatureSource:
    return __feature_container
