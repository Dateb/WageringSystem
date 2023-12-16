from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import previous_momentum_source, dam_and_sire_average_momentum_source


class PreviousMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()
        previous_momentum_source.previous_value_attribute_groups.append(["subject_id"])

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_momentum = previous_momentum_source.get_previous_of_name(str(horse.subject_id))

        if previous_momentum is None:
            return self.PLACEHOLDER_VALUE

        return previous_momentum


class SireMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()
        dam_and_sire_average_momentum_source.average_attribute_groups.append(["name"])

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_momentum = dam_and_sire_average_momentum_source.get_average_of_name(horse.sire)

        if average_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return average_momentum


class DamMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        average_momentum = dam_and_sire_average_momentum_source.get_average_of_name(horse.dam)

        if average_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return average_momentum
