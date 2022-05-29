from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PostPositionExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Post_Position_{self.__race_card_idx}"

    def get_value(self, horse: Horse) -> int:
        if self.__race_card_idx >= horse.n_races:
            return self.PLACEHOLDER_VALUE

        race_card = horse.get_race(self.__race_card_idx)
        post_position = race_card.post_position_of_horse(horse.subject_id)

        if post_position == -1:
            return self.PLACEHOLDER_VALUE

        return post_position
