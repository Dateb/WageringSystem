from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class DistanceDifference(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        # TODO: differs by -1 for some reason
        return get_difference_of_current_and_previous_attribute_value(race_card, horse, "distance")


class RaceClassDifference(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_difference_of_current_and_previous_attribute_value(race_card, horse, "race_class")


class HasJockeyChanged(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        current_jockey_last_name = horse.jockey.last_name

        if not horse.form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_form = horse.form_table.past_forms[0]
        if not previous_form.jockey_name:
            return self.PLACEHOLDER_VALUE

        # TODO: Why?
        if len(previous_form.jockey_name.split(" ")) < 2:
            return self.PLACEHOLDER_VALUE

        previous_jockey_last_name = previous_form.jockey_name.split(" ")[1]

        return previous_jockey_last_name != current_jockey_last_name


def get_difference_of_current_and_previous_attribute_value(race_card: RaceCard, horse: Horse, attribute_name: str):
    try:
        current_attribute_value = float(getattr(race_card, attribute_name))

        form_table = horse.form_table
        if not horse.form_table.past_forms:
            return float('NaN')

        previous_form = form_table.past_forms[0]
        previous_attribute_value = float(getattr(previous_form, attribute_name))
    except ValueError:
        return float('NaN')

    # TODO: fix small distance differences
    # if current_attribute_value - previous_attribute_value == -1 and attribute_name == "distance":
    #     print(f"current:{current_attribute_value}")
    #     print(f"previous:{previous_attribute_value}")

    return current_attribute_value - previous_attribute_value
