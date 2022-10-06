from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Sources.FeatureSource import FeatureSource
from util.nested_dict import nested_dict


class WinRateSource(FeatureSource):

    def __init__(self):
        super().__init__()
        self.__win_rates = nested_dict()
        self.win_rate_attribute_groups = []

    def update(self, race_card: RaceCard):
        for horse in race_card.horses:
            for win_rate_attribute_group in self.win_rate_attribute_groups:
                win_rate_attribute_group_name = ""
                for win_rate_attribute in win_rate_attribute_group:
                    win_rate_name = getattr(horse, win_rate_attribute)
                    win_rate_attribute_group_name += f"{win_rate_name}_"

                win_rate_attribute_group_name = win_rate_attribute_group_name[:-1]
                self.update_average(self.__win_rates[win_rate_attribute_group_name], horse.has_won, race_card.date)

    def get_win_rate_of_name(self, name: str) -> float:
        win_rate = self.__win_rates[name]
        if "avg" in win_rate and win_rate["count"] >= 5:
            return win_rate["avg"]
        return -1


win_rate_source: WinRateSource = WinRateSource()
