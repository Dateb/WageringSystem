from abc import abstractmethod
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard


class FeatureSource:

    def __init__(self):
        self.alpha = 0.125

    def warmup(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.update(race_card)

    @abstractmethod
    def update(self, race_card: RaceCard):
        pass

    def update_average(self, category: dict, new_obs: float) -> None:
        if "avg" not in category:
            category["avg"] = new_obs
            category["count"] = 1
        else:
            category["avg"] = self.alpha * new_obs + (1 - self.alpha) * category["avg"]
            category["count"] += 1


__feature_container: FeatureSource = FeatureSource()


def get_feature_source() -> FeatureSource:
    return __feature_container
