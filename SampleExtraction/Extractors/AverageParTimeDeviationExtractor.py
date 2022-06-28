import math

from SampleExtraction.Container import ParTimesContainer
from SampleExtraction.Container.FeatureContainer import FeatureContainer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Horse import Horse


class AverageParTimeDeviationExtractor(FeatureExtractor):

    def __init__(self, n_races_ago: int):
        super().__init__()
        self.__par_times_container = ParTimesContainer.get_feature_container()
        self.__n_races_ago = n_races_ago

    def get_name(self) -> str:
        return "Average_Par_Time_Deviation"

    def get_value(self, horse: Horse) -> float:
        if not horse.has_past_races:
            return self.PLACEHOLDER_VALUE

        base_race_card = horse.get_race(0)
        form_table = base_race_card.form_table_of_horse(horse.horse_id)
        n_past_races = min([self.__n_races_ago, len(form_table)])
        past_races = [form_table[race_idx] for race_idx in range(n_past_races)]
        par_time_deviations = [self.__get_par_time_deviation(horse, past_race) for past_race in past_races]
        valid_par_time_deviations = [
            par_time_deviation for par_time_deviation in par_time_deviations
            if not math.isnan(par_time_deviation)
        ]

        if not valid_par_time_deviations:
            return self.PLACEHOLDER_VALUE

        return sum(valid_par_time_deviations) / len(valid_par_time_deviations)

    def __get_par_time_deviation(self, horse: Horse, past_race: dict) -> float:
        base_race_card = horse.get_race(0)
        past_time = base_race_card.time_of_past_race(past_race)

        past_distance = past_race["raceDistance"]
        past_class = past_race["categoryLetter"]
        past_par_time = self.__par_times_container.par_time(past_class, past_distance)

        if past_time == -1 or past_par_time == -1:
            return self.PLACEHOLDER_VALUE

        return (past_time - past_par_time) / past_par_time

    @property
    def container(self) -> FeatureContainer:
        return self.__par_times_container
