from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class SireSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__horse_win_rate = nested_dict()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.update_average(self.__horse_win_rate[horse.name], horse.has_won, race_card.date)

    def get_sire_win_rate(self, child_horse: Horse) -> float:
        sire_data = self.__horse_win_rate[child_horse.sire]
        if "avg" in sire_data:
            return sire_data["avg"]
        return -1


__feature_source: SireSource = SireSource()


def get_feature_source() -> SireSource:
    return __feature_source
