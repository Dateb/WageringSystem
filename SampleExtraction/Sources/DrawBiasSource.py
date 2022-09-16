from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class DrawBiasSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__draw_bias = nested_dict()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            post_position = str(horse.post_position)
            if post_position != "-1":
                self.update_average(self.__draw_bias[race_card.track_name][post_position], horse.has_won)

    def draw_bias(self, track_name: str, post_position: int):
        if track_name not in self.__draw_bias or str(post_position) not in self.__draw_bias[track_name]:
            return -1
        return self.__draw_bias[track_name][str(post_position)]["avg"]


__feature_source: DrawBiasSource = DrawBiasSource()


def get_feature_source() -> DrawBiasSource:
    return __feature_source
