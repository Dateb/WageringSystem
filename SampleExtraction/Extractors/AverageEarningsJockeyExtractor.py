from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class AverageEarningsJockeyExtractor(FeatureExtractor):

    def __init__(self, race_card_idx: int = 0):
        self.__race_card_idx = race_card_idx
        super().__init__()

    def get_name(self) -> str:
        return f"Average_Earnings_Jockey_{self.__race_card_idx}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if self.__race_card_idx >= horse.n_races:
            return self.PLACEHOLDER_VALUE

        race_card = horse.get_race(self.__race_card_idx)
        jockey_earnings = race_card.jockey_earnings_of_horse(horse.subject_id)
        jockey_num_races = race_card.jockey_num_races_of_horse(horse.subject_id)
        if jockey_earnings == -1:
            return self.PLACEHOLDER_VALUE
        return jockey_earnings / jockey_num_races
