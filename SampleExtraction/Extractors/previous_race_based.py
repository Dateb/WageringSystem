from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import previous_odds_source


class PreviousWinProbability(FeatureExtractor):

    previous_odds_source.previous_value_attribute_groups.append(["name"])
    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        # previous_exchange_odds = previous_odds_source.get_previous_of_name(horse.name)
        # if previous_exchange_odds not in [-1, 0]:
        #     return 1 / previous_exchange_odds

        past_forms = horse.form_table.past_forms
        if not past_forms:
            return self.PLACEHOLDER_VALUE
        previous_form = past_forms[0]

        if not previous_form.odds:
            return self.PLACEHOLDER_VALUE

        return 1 / previous_form.odds


class PreviousRelativeDistanceBehind(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms = horse.form_table.past_forms
        if not past_forms:
            return self.PLACEHOLDER_VALUE
        previous_form = past_forms[0]

        if not previous_form.distance:
            return self.PLACEHOLDER_VALUE

        return previous_form.horse_distance / previous_form.distance


class PreviousFasterThanNumber(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE
        return abs(int(horse.previous_performance) - race_card.n_horses) / (race_card.n_horses - 1)


class PreviousSlowerThanNumber(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE
        return abs(int(horse.previous_performance) - 1) / (race_card.n_horses - 1)


class PulledUpPreviousRace(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.previous_performance == "PU")
