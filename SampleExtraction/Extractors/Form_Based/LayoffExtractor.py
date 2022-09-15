from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class LayoffExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.base_name = "Layoff"
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return f"{self.base_name}_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        form_table = horse.form_table
        if len(form_table.past_forms) < self.__n_races_ago + 1:
            return self.PLACEHOLDER_VALUE

        if self.__n_races_ago == 0:
            current_date = race_card.date
        else:
            current_date = horse.form_table.past_forms[self.__n_races_ago - 1].date
        previous_date = horse.form_table.past_forms[self.__n_races_ago].date

        return (current_date - previous_date).days
