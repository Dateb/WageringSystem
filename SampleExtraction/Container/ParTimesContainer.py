from typing import List

from DataAbstraction.RaceCard import RaceCard
from SampleExtraction.Container.FeatureContainer import FeatureContainer


class ParTimesContainer(FeatureContainer):

    def __init__(self):
        super().__init__()
        self.__par_times = {}

    def fit(self, train_race_cards: List[RaceCard]):
        for race_card in train_race_cards:
            for horse in race_card.horses:
                for past_race in race_card.form_table_of_horse(horse):
                    race_class = past_race["categoryLetter"]
                    race_distance = str(past_race["raceDistance"])
                    par_time_key = (race_class, race_distance)

                    new_obs = past_race["winTimeSeconds"]
                    if new_obs > 0:
                        if par_time_key not in self.__par_times:
                            self.__par_times[par_time_key] = {"avg": new_obs, "count": 1}
                        else:
                            self.__par_times[par_time_key]["count"] += 1
                            new_count = self.__par_times[par_time_key]["count"]
                            old_avg = self.__par_times[par_time_key]["avg"]

                            new_avg = old_avg + (new_obs - old_avg) / new_count
                            self.__par_times[par_time_key]["avg"] = new_avg

    def par_time(self, race_class: str, race_distance: int):
        par_time_key = (race_class, str(race_distance))
        if par_time_key not in self.__par_times or race_class == '':
            return -1
        return self.__par_times[(race_class, str(race_distance))]["avg"]


__feature_container: ParTimesContainer = ParTimesContainer()


def get_feature_container() -> ParTimesContainer:
    return __feature_container
