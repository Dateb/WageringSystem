from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources import DrawBiasSource
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PastDrawBiasExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.base_name = "Draw_Bias"
        self.__n_races_ago = n_races_ago
        self.source = DrawBiasSource.get_feature_source()

    def get_name(self) -> str:
        return f"{self.base_name}_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if self.__n_races_ago > len(horse.form_table.past_forms):
            return self.PLACEHOLDER_VALUE

        past_track_name = horse.form_table.past_forms[self.__n_races_ago - 1].track_name
        past_post_position = horse.form_table.past_forms[self.__n_races_ago - 1].post_position

        draw_bias = self.source.draw_bias(past_track_name, past_post_position)

        if draw_bias == -1:
            return self.PLACEHOLDER_VALUE

        return draw_bias
