from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Container.FeatureContainer import FeatureContainer


class DrawBiasContainer(FeatureContainer):

    def __init__(self):
        super().__init__()
        self.__draw_bias = {}

    def fit(self, train_race_cards: List[RaceCard]):
        for race_card in train_race_cards:
            if race_card.track_name not in self.__draw_bias:
                self.__draw_bias[race_card.track_name] = {}

            race_card_bias = self.__draw_bias[race_card.track_name]
            for horse in race_card.horses:
                post_position = str(horse.post_position)
                if post_position != "-1":
                    new_obs = 0
                    if horse.has_won:
                        new_obs = 1

                    if post_position not in race_card_bias:
                        race_card_bias[post_position] = {"avg": new_obs, "count": 1}
                    else:
                        race_card_bias[post_position]["count"] += 1
                        new_count = race_card_bias[post_position]["count"]
                        old_avg = race_card_bias[post_position]["avg"]

                        new_avg = old_avg + (new_obs - old_avg) / new_count
                        race_card_bias[post_position]["avg"] = new_avg
        print(self.__draw_bias)

    def draw_bias(self, track_name: str, post_position: int):
        if track_name not in self.__draw_bias:
            return -1
        if str(post_position) not in self.__draw_bias[track_name]:
            return -1
        return self.__draw_bias[track_name][str(post_position)]["avg"]


__feature_container: DrawBiasContainer = DrawBiasContainer()


def get_feature_container() -> DrawBiasContainer:
    return __feature_container
