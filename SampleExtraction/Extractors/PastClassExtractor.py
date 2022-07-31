from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PastClassExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.base_name = "Past_Class"
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return f"{self.base_name}_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if self.__n_races_ago > len(horse.form_table.past_forms):
            return self.PLACEHOLDER_VALUE

        past_class = horse.form_table.past_forms[self.__n_races_ago - 1].race_class

        try:
            past_class = int(past_class)
        except ValueError:
            past_class = self.PLACEHOLDER_VALUE

        return past_class
