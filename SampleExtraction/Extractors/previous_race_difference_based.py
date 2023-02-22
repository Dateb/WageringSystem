from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import previous_distance_source, previous_trainer_source


class DistanceDifference(FeatureExtractor):

    previous_distance_source.previous_value_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_distance = previous_distance_source.get_previous_of_name(horse.name)
        if previous_distance == -1:
            return self.PLACEHOLDER_VALUE

        return race_card.distance - previous_distance


class RaceClassDifference(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_difference_of_current_and_previous_attribute_value(race_card, horse, "race_class")


class HasTrainerChanged(FeatureExtractor):
    previous_trainer_source.previous_value_attribute_groups.append(["name"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_trainer_name = previous_trainer_source.get_previous_of_name(horse.name)
        if previous_trainer_name == -1:
            return self.PLACEHOLDER_VALUE

        return int(horse.trainer_name != previous_trainer_name)


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

        if len(previous_form.jockey_name.split(" ")) < 2:
            return self.PLACEHOLDER_VALUE

        previous_jockey_last_name = previous_form.jockey_name.split(" ")[1]

        return previous_jockey_last_name != current_jockey_last_name


class HasTrackChanged(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        form_table = horse.form_table

        if not form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_track = form_table.past_forms[0].track_name
        current_track = race_card.track_name

        return int(previous_track != current_track)


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

    return current_attribute_value - previous_attribute_value
