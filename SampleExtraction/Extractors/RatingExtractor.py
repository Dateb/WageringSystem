from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class RatingExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Rating_{self.__n_races_ago}"

    def get_value(self, horse: Horse) -> float:
        race_card = horse.get_race(0)
        rating = race_card.rating_of_horse(horse.horse_id)
        if rating == -1:
            return self.PLACEHOLDER_VALUE
        return rating
