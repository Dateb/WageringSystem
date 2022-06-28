from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class WinRateJockeyExtractor(FeatureExtractor):

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Win_Rate_Jockey_{self.__race_card_idx}"

    def get_value(self, horse: Horse) -> float:
        if self.__race_card_idx >= horse.n_races:
            return self.PLACEHOLDER_VALUE

        race_card = horse.get_race(self.__race_card_idx)
        jockey_wins = race_card.jockey_wins_of_horse(horse.subject_id)
        jockey_num_races = race_card.jockey_num_races_of_horse(horse.subject_id)
        if jockey_wins == -1:
            return self.PLACEHOLDER_VALUE
        return jockey_wins / jockey_num_races
