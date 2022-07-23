from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class WinRateTrainerExtractor(FeatureExtractor):

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Win_Rate_Trainer_{self.__race_card_idx}"

    def get_value(self, horse: Horse) -> float:
        if self.__race_card_idx >= horse.n_races:
            return self.PLACEHOLDER_VALUE

        race_card = horse.get_race(self.__race_card_idx)
        trainer_wins = race_card.trainer_wins_of_horse(horse.subject_id)
        trainer_num_races = race_card.trainer_num_races_of_horse(horse.subject_id)
        if trainer_wins == -1:
            return self.PLACEHOLDER_VALUE
        return trainer_wins / trainer_num_races
