from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class AverageEarningsTrainerExtractor(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Earnings_Trainer_{self.__race_card_idx}"

    def get_value(self, horse: Horse) -> float:
        if self.__race_card_idx >= horse.n_races:
            return self.PLACEHOLDER_VALUE

        race_card = horse.get_race(self.__race_card_idx)
        trainer_earnings = race_card.trainer_earnings_of_horse(horse.subject_id)
        trainer_num_races = race_card.trainer_num_races_of_horse(horse.subject_id)
        if trainer_earnings == -1:
            return self.PLACEHOLDER_VALUE
        return trainer_earnings / trainer_num_races
