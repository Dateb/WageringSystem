from abc import abstractmethod
from typing import List

from DataAbstraction.Present.RaceCard import RaceCard


class FeatureContainer:

    def __init__(self):
        pass

    @abstractmethod
    def fit(self, train_race_cards: List[RaceCard]):
        pass


__feature_container: FeatureContainer = FeatureContainer()


def get_feature_container() -> FeatureContainer:
    return __feature_container
