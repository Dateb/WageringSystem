from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class JockeyCurrentHorsePurseExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Jockey_Current_Horse_Purse_Extractor"

    def get_value(self, horse: Horse) -> float:
        base_race_card = horse.get_race(0)
        current_jockey_last_name = base_race_card.jockey_last_name_of_horse(horse.horse_id)

        past_purses_of_current_jockey_and_horse = base_race_card.purse_history_of_horse_and_jockey(
            horse.horse_id,
            current_jockey_last_name
        )

        if not past_purses_of_current_jockey_and_horse:
            return self.PLACEHOLDER_VALUE

        return sum(past_purses_of_current_jockey_and_horse)
