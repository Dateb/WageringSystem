from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AverageEarningsTrainerExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int = 0):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Earnings_Trainer_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if self.__n_races_ago == 0:
            trainer_earnings = horse.trainer.earnings
            mean_earnings = horse.trainer.earnings / horse.trainer.num_races
        else:
            if self.__n_races_ago > horse.n_past_races:
                return self.PLACEHOLDER_VALUE

            past_race = horse.past_races[self.__n_races_ago - 1]
            past_trainer = past_race.get_subject(horse.subject_id).trainer
            trainer_earnings = past_trainer.earnings
            mean_earnings = trainer_earnings / past_trainer.num_races

        if trainer_earnings == -1:
            return self.PLACEHOLDER_VALUE

        return mean_earnings
