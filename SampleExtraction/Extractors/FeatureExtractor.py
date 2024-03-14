from abc import abstractmethod, ABC
from typing import Any, List

from DataAbstraction.Present.RaceCard import RaceCard
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.feature_sources import FeatureSource, FeatureValueGroup, PreviousValueSource, \
    PreviousValueScratchedSource
from SampleExtraction.feature_sources.value_calculators import race_date


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

    def __init__(
            self,
            feature_source: FeatureSource,
            update_feature_value_group: FeatureValueGroup,
            read_feature_value_group: FeatureValueGroup = None
    ):
        super().__init__()
        self.feature_source = feature_source
        self.update_feature_value_group = update_feature_value_group

        self.feature_source.register_feature_value_group(update_feature_value_group)

        self.read_feature_value_group = update_feature_value_group
        if read_feature_value_group is not None:
            self.read_feature_value_group = read_feature_value_group

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        feature_value = self.feature_source.get_feature_value(race_card, horse, self.read_feature_value_group)

        if feature_value is None:
            return self.PLACEHOLDER_VALUE

        return feature_value

    def get_name(self) -> str:
        name = f"{self.feature_source.get_name()}_{self.update_feature_value_group.name}"
        if self.read_feature_value_group != self.update_feature_value_group:
            name += f"_{self.read_feature_value_group.name}"
        return name


class LayoffExtractor(FeatureExtractor):

    def __init__(self, previous_value_source: PreviousValueSource, horse_attributes: List[str], race_card_attributes: List[str]):
        super().__init__()
        self.feature_source = previous_value_source
        self.feature_value_group = FeatureValueGroup(race_date, horse_attributes, race_card_attributes)

        self.feature_source.register_feature_value_group(self.feature_value_group)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_date = self.feature_source.get_feature_value(race_card, horse, self.feature_value_group)

        if previous_date is None:
            return self.PLACEHOLDER_VALUE

        layoff = (race_card.date - previous_date).days
        return layoff

    def get_name(self) -> str:
        return f"{self.feature_source.get_name()}_{self.feature_value_group.name}"


class TimeSinceNotEatenUp(FeatureExtractor):

    def __init__(self, previous_value_source: PreviousValueScratchedSource, attributes: List[str]):
        super().__init__()
        self.feature_source = previous_value_source
        self.feature_value_group = FeatureValueGroup(attributes, race_date)

        self.feature_source.register_feature_value_group(self.feature_value_group)

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        original_not_eaten_up_val = horse.not_eaten_up
        horse.not_eaten_up = True
        previous_date = self.feature_source.get_feature_value(race_card, horse, self.feature_value_group)
        horse.not_eaten_up = original_not_eaten_up_val

        if previous_date is None:
            return self.PLACEHOLDER_VALUE

        time_since_not_eaten_up = (race_card.date - previous_date).days
        return time_since_not_eaten_up

    def get_name(self) -> str:
        return f"{self.feature_source.get_name()}_{self.feature_value_group.name}"