from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import DrawBiasSource
from SampleExtraction.Sources.FeatureSource import FeatureSource
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class DrawBiasExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__draw_bias_container = DrawBiasContainer.get_feature_source()

    def get_name(self) -> str:
        return "Draw_Bias"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        draw_bias = self.__draw_bias_container.draw_bias(race_card.track_name, horse.post_position)
        if draw_bias == -1:
            return self.PLACEHOLDER_VALUE
        return draw_bias

    @property
    def container(self) -> FeatureSource:
        return self.__draw_bias_container
