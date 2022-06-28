from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AverageRatingExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return "Average_Rating"

    def get_value(self, horse: Horse) -> float:
        race_card = horse.get_race(0)
        past_ratings = [
            race_card.horse_rating_n_races_ago(horse.horse_id, race_idx) for race_idx in range(0, self.__n_races_ago)
        ]
        past_valid_ratings = [rating for rating in past_ratings if rating != -1]

        if not past_valid_ratings:
            return self.PLACEHOLDER_VALUE

        return sum(past_valid_ratings) / len(past_valid_ratings)
