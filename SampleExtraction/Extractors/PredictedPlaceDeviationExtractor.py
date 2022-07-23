from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class PredictedPlaceDeviationExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        self.__n_races_ago = n_races_ago
        super().__init__()

    def get_name(self) -> str:
        return f"Predicted_Place_Deviation_{self.__n_races_ago}"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if self.__n_races_ago > horse.n_past_races:
            return self.PLACEHOLDER_VALUE

        past_race = horse.past_races[self.__n_races_ago - 1]
        horse_past_race = [past_horse for past_horse in past_race.horses if past_horse.subject_id == horse.subject_id][0]

        if horse_past_race.place == -1:
            return self.PLACEHOLDER_VALUE

        horse_past_odds = horse_past_race.current_odds
        past_race_odds = [horse.current_odds for horse in past_race.horses]

        lower_odds = [odds for odds in past_race_odds if odds < horse_past_odds]

        predicted_place = 1 + len(lower_odds)
        actual_place = horse_past_race.place

        return predicted_place - actual_place
