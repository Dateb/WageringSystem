from SampleExtraction.Container import ParTimesContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class ParTimeDeviationSameTrack(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.__par_times_container = ParTimesContainer.get_feature_container()

    def get_name(self) -> str:
        return "Par_Time_Deviation_Same_Track"

    def get_value(self, horse: Horse) -> int:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)

        past_times = base_race_card.past_times_of_horse_same_track(horse.horse_id)
        latest_race_idx = next((idx for idx, past_time in enumerate(past_times) if past_time > 0), None)

        if latest_race_idx is None:
            return self.PLACEHOLDER_VALUE

        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        past_race = form_table[latest_race_idx]
        past_distance = past_race["raceDistance"]
        past_class = past_race["categoryLetter"]

        past_par_time = self.__par_times_container.par_time(past_class, past_distance)
        past_time = past_times[latest_race_idx]

        if past_par_time == -1:
            return self.PLACEHOLDER_VALUE

        same_track_par_time_deviation = (past_time - past_par_time) / past_par_time

        return same_track_par_time_deviation

    @property
    def container(self) -> FeatureContainer:
        return self.__par_times_container
