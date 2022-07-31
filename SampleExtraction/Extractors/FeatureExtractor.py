from abc import abstractmethod, ABC
from typing import Any

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Container import FeatureContainer
from DataAbstraction.Present.Horse import Horse


class FeatureExtractor(ABC):

    PLACEHOLDER_VALUE = float('NaN')

    def __init__(self):
        self.base_name = "default"

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self, race_card: RaceCard, horse: Horse) -> Any:
        pass

    @property
    def container(self) -> FeatureContainer:
        return FeatureContainer.get_feature_container()
