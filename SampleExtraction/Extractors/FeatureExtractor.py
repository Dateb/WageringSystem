from abc import abstractmethod, ABC
from typing import Any

from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.feature_sources import FeatureSource, FeatureValueGroup


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


class FeatureSourceExtractor(FeatureExtractor):

    def __init__(self, feature_source: FeatureSource, feature_value_group: FeatureValueGroup):
        super().__init__()
        self.feature_source = feature_source
        self.feature_value_group = feature_value_group

        self.feature_source.register_feature_value_group(feature_value_group)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        feature_value = self.feature_source.get_feature_value(race_card, horse, self.feature_value_group)

        if feature_value is None:
            return self.PLACEHOLDER_VALUE

        return feature_value

    def get_name(self) -> str:
        return f"{self.feature_source.get_name()}_{self.feature_value_group.name}"
