from SampleExtraction.Container import DrawBiasContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class DrawBiasExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__draw_bias_container = DrawBiasContainer.get_feature_container()

    def get_name(self) -> str:
        return "Draw_Bias"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)

        return self.__draw_bias_container.draw_bias(
            base_race_card.title,
            base_race_card.post_position_of_horse(horse.subject_id)
        )

    @property
    def container(self) -> FeatureContainer:
        return self.__draw_bias_container
