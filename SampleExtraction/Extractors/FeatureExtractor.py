from abc import abstractmethod, ABC
from typing import Any

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import FeatureSource
from DataAbstraction.Present.Horse import Horse


class FeatureExtractor(ABC):

    PLACEHOLDER_VALUE = float('NaN')

    def __init__(self):
        self.base_name = "default"
        self.source = FeatureSource.get_feature_source()
        self.is_categorical = False

    def __str__(self) -> str:
        return self.get_name()

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self, race_card: RaceCard, horse: Horse) -> Any:
        pass
