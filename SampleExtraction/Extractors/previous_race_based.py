from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import previous_win_prob_source


class PreviousWinProbability(FeatureExtractor):

    previous_win_prob_source.previous_value_attribute_groups.append(["name"])
    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return previous_win_prob_source.get_previous_of_name(horse.name) + 1
        # if previous_exchange_odds not in [-1, 0]:
        #     return 1 / previous_exchange_odds
        #
        # past_forms = horse.form_table.past_forms
        # if not past_forms:
        #     return self.PLACEHOLDER_VALUE
        # previous_form = past_forms[0]
        #
        # if not previous_form.odds:
        #     return self.PLACEHOLDER_VALUE
        #
        # return 1 / previous_form.odds


class PreviousPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        past_forms = horse.form_table.past_forms
        if not past_forms:
            return self.PLACEHOLDER_VALUE

        previous_n_horses = past_forms[0].n_horses
        previous_performance = horse.previous_performance

        if previous_performance == "PU":
            previous_performance = str(previous_n_horses)

        if not previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE

        if previous_n_horses == 1:
            if len(past_forms) == 1:
                return self.PLACEHOLDER_VALUE

            previous_n_horses = past_forms[1].n_horses
            previous_performance = past_forms[1].final_position

            if previous_performance == -1:
                return self.PLACEHOLDER_VALUE

        previous_place = int(previous_performance)

        return (previous_place - 1) / (previous_n_horses - 1) + 1


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

        if previous_form.horse_distance == -1:
            return self.PLACEHOLDER_VALUE

        return previous_form.horse_distance / previous_form.distance


class PreviousFasterThanFraction(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE

        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_n_horses = horse.form_table.past_forms[0].n_horses

        if previous_n_horses == 1:
            return self.PLACEHOLDER_VALUE

        return abs(int(horse.previous_performance) - 1) / (previous_n_horses - 1) + 1


class PreviousSlowerThanFraction(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not horse.previous_performance.isnumeric():
            return self.PLACEHOLDER_VALUE

        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_n_horses = horse.form_table.past_forms[0].n_horses

        if previous_n_horses == 1:
            return self.PLACEHOLDER_VALUE

        return abs(previous_n_horses - int(horse.previous_performance)) / (previous_n_horses - 1) + 1


class PulledUpPreviousRace(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.previous_performance == "PU")
