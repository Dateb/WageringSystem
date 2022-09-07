from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PastWeightExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.__n_races_ago = n_races_ago
        self.base_name = "Weight"

    def get_name(self) -> str:
        return f"{self.base_name}_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if len(horse.form_table.past_forms) < self.__n_races_ago:
            return self.PLACEHOLDER_VALUE

        past_weight = horse.form_table.past_forms[self.__n_races_ago - 1].weight

        if past_weight == -1:
            return self.PLACEHOLDER_VALUE

        return past_weight
