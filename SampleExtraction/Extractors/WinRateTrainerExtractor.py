from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class WinRateTrainerExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int = 0):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Win_Rate_Trainer_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if self.__n_races_ago == 0:
            win_rate = horse.trainer.win_rate
        else:
            if self.__n_races_ago > horse.n_past_races:
                return self.PLACEHOLDER_VALUE

            past_race = horse.past_races[self.__n_races_ago - 1]
            win_rate = past_race.get_subject(horse.subject_id).trainer.win_rate

        if win_rate == -1:
            return self.PLACEHOLDER_VALUE

        return win_rate
