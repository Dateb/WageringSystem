from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class DistanceDifference(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Distance_Difference"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        # TODO: differs by -1 for some reason
        return get_difference_of_current_and_previous_attribute_value(race_card, horse, "distance")


class RaceClassDifference(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Class_Difference"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_difference_of_current_and_previous_attribute_value(race_card, horse, "race_class")


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

    # if current_attribute_value - previous_attribute_value == -1 and attribute_name == "distance":
    #     print(f"current:{current_attribute_value}")
    #     print(f"previous:{previous_attribute_value}")

    return current_attribute_value - previous_attribute_value
