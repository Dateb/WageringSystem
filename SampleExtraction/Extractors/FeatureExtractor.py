from abc import abstractmethod, ABC


class FeatureExtractor(ABC):

    PLACEHOLDER_VALUE: str = "0"

    def __init__(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self, horse_id: str, horse_data: dict) -> int:
        pass
