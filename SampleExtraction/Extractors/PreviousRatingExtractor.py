from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class PreviousRatingExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return "Previous_Rating"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        return horse.form_table.past_forms[0].rating
