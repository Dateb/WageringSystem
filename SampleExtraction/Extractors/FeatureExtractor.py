from abc import abstractmethod, ABC
from typing import Any

from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Horse import Horse


class FeatureExtractor(ABC):

    PLACEHOLDER_VALUE = float('NaN')

    def __init__(self):
        self.base_name = "default"
        self.is_categorical = False

    def __str__(self) -> str:
        return self.get_name()

    def get_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def get_value(self, race_card: RaceCard, horse: Horse) -> Any:
        pass
