from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class NamedWinRateSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__win_rates = nested_dict()

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            self.update_average(self.__win_rates[horse.breeder], horse.has_won)
            self.update_average(self.__win_rates[horse.owner], horse.has_won)

    def get_win_rate_of_name(self, name: str) -> float:
        win_rate = self.__win_rates[name]
        if "avg" in win_rate and win_rate["count"] >= 5:
            return win_rate["avg"]
        return -1


__feature_source: NamedWinRateSource = NamedWinRateSource()


def get_feature_source() -> NamedWinRateSource:
    return __feature_source
