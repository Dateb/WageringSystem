from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AverageEarningsJockeyExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int = 0):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Earnings_Jockey_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if self.__n_races_ago == 0:
            jockey_earnings = horse.jockey.earnings
            mean_earnings = horse.jockey.earnings / horse.jockey.num_races
        else:
            if self.__n_races_ago > horse.n_past_races:
                return self.PLACEHOLDER_VALUE

            past_race = horse.past_races[self.__n_races_ago - 1]
            past_jockey = past_race.get_subject(horse.subject_id).jockey
            jockey_earnings = past_jockey.earnings
            mean_earnings = jockey_earnings / past_jockey.num_races

        if jockey_earnings == -1:
            return self.PLACEHOLDER_VALUE
        return mean_earnings
