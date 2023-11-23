from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import previous_velocity_source, dam_and_sire_average_velocity_source


class PreviousVelocity(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()
        previous_velocity_source.previous_value_attribute_groups.append(["subject_id"])

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_velocity = previous_velocity_source.get_previous_of_name(str(horse.subject_id))

        if previous_velocity is None:
            return self.PLACEHOLDER_VALUE

        return previous_velocity / 25


class SireVelocity(FeatureExtractor):

    def __init__(self):
        super().__init__()
        dam_and_sire_average_velocity_source.average_attribute_groups.append(["name"])

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_velocity = dam_and_sire_average_velocity_source.get_average_of_name(horse.sire)

        if average_velocity == -1:
            return self.PLACEHOLDER_VALUE

        return average_velocity / 25


class DamVelocity(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_velocity = dam_and_sire_average_velocity_source.get_average_of_name(horse.dam)

        if average_velocity == -1:
            return self.PLACEHOLDER_VALUE

        return average_velocity / 25
