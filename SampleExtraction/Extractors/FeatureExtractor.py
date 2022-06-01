from abc import abstractmethod, ABC

from SampleExtraction.Horse import Horse


class FeatureExtractor(ABC):

    PLACEHOLDER_VALUE = float('NaN')

    def __init__(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_value(self, horse: Horse) -> int:
        pass
