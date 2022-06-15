from SampleExtraction.Container import ParTimesContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Horse import Horse


class PastParTimeDeviationExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.__par_times_container = ParTimesContainer.get_feature_container()
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return f"Past_Par_Time_Deviation_{self.__n_races_ago}"

    def get_value(self, horse: Horse) -> int:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)
        form_table = base_race_card.form_table_of_horse(horse.horse_id)

        if len(form_table) < self.__n_races_ago:
            return self.PLACEHOLDER_VALUE

        past_race = form_table[self.__n_races_ago - 1]
        past_distance = past_race["raceDistance"]
        past_class = past_race["categoryLetter"]

        past_par_time = self.__par_times_container.par_time(past_class, past_distance)
        past_time = base_race_card.past_times_of_horse(horse.horse_id)[self.__n_races_ago - 1]

        if past_time == -1 or past_par_time == -1:
            return self.PLACEHOLDER_VALUE

        previous_par_time_deviation = (past_time - past_par_time) / past_par_time

        return previous_par_time_deviation

    @property
    def container(self) -> FeatureContainer:
        return self.__par_times_container
