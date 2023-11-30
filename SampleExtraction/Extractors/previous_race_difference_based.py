from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.init import previous_distance_source, previous_race_going_source, \
    previous_race_class_source, previous_trainer_source, previous_jockey_source, win_rate_source, previous_owner_source


class DistanceDifference(FeatureExtractor):

    previous_distance_source.previous_value_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_distance = previous_distance_source.get_previous_of_name(str(horse.subject_id))
        if previous_distance is None:
            return self.PLACEHOLDER_VALUE

        return (race_card.distance / previous_distance)


class RaceGoingDifference(FeatureExtractor):

    previous_race_going_source.previous_value_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_race_going = previous_race_going_source.get_previous_of_name(str(horse.subject_id))
        if previous_race_going is None:
            return self.PLACEHOLDER_VALUE

        return (race_card.going - previous_race_going)


class RaceClassDifference(FeatureExtractor):

    previous_race_class_source.previous_value_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_race_class = previous_race_class_source.get_previous_of_name(str(horse.subject_id))
        if previous_race_class is None:
            return self.PLACEHOLDER_VALUE

        if race_card.race_class in ["A", "B"] or previous_race_class in ["A", "B"]:
            return self.PLACEHOLDER_VALUE

        race_class_difference = int(race_card.race_class) - int(previous_race_class)

        return race_class_difference


class HasTrainerChanged(FeatureExtractor):
    previous_trainer_source.previous_value_attribute_groups.append(["name"])

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_trainer_name = previous_trainer_source.get_previous_of_name(horse.name)
        if previous_trainer_name == -1:
            return self.PLACEHOLDER_VALUE

        return int(horse.trainer_name != previous_trainer_name) + 1


class HasJockeyChanged(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

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

        return (previous_jockey_last_name != current_jockey_last_name) + 1


class IsSecondRaceForJockey(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        current_jockey_last_name = horse.jockey.last_name

        if len(horse.form_table.past_forms) < 2:
            return self.PLACEHOLDER_VALUE

        previous_form = horse.form_table.past_forms[0]
        penultimate_form = horse.form_table.past_forms[1]

        if not previous_form.jockey_name or not penultimate_form.jockey_name:
            return self.PLACEHOLDER_VALUE

        if len(previous_form.jockey_name.split(" ")) < 2 or len(penultimate_form.jockey_name.split(" ")) < 2:
            return self.PLACEHOLDER_VALUE

        previous_race_jockey_change = previous_form.jockey_name.split(" ")[1] != penultimate_form.jockey_name.split(" ")[1]
        current_race_no_jockey_change = current_jockey_last_name == previous_form.jockey_name.split(" ")[1]

        return previous_race_jockey_change and current_race_no_jockey_change


class HasTrackChanged(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        form_table = horse.form_table

        if not form_table.past_forms:
            return self.PLACEHOLDER_VALUE

        previous_track = form_table.past_forms[0].track_name
        current_track = race_card.track_name

        return int(previous_track != current_track)


class WeightDifference(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_weight = horse.jockey.weight

        if current_weight < 0:
            return self.PLACEHOLDER_VALUE

        previous_jockey = previous_jockey_source.get_previous_of_name(str(horse.subject_id))

        if previous_jockey is None:
            return self.PLACEHOLDER_VALUE

        previous_weight = previous_jockey.weight

        if previous_weight < 0:
            return self.PLACEHOLDER_VALUE

        return current_weight - previous_weight


class AllowanceDifference(FeatureExtractor):

    PLACEHOLDER_VALUE = 0

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_allowance = horse.jockey.allowance

        if current_allowance < 0:
            return self.PLACEHOLDER_VALUE

        previous_jockey = previous_jockey_source.get_previous_of_name(str(horse.subject_id))

        if previous_jockey is None:
            return self.PLACEHOLDER_VALUE

        previous_allowance = previous_jockey.allowance

        if previous_allowance < 0:
            return self.PLACEHOLDER_VALUE

        return current_allowance - previous_allowance


class OwnerWinRateDifference(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        current_owner_win_rate = win_rate_source.get_average_of_name(horse.owner)

        if current_owner_win_rate == -1:
            return self.PLACEHOLDER_VALUE

        previous_owner = previous_owner_source.get_previous_of_name(str(horse.subject_id))

        if previous_owner is None:
            return self.PLACEHOLDER_VALUE

        previous_owner_win_rate = win_rate_source.get_average_of_name(previous_owner)

        if previous_owner_win_rate == -1:
            return self.PLACEHOLDER_VALUE

        win_rate_difference = (current_owner_win_rate - previous_owner_win_rate) / 2 + 0.5

        return win_rate_difference


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
