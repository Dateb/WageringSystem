from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.init import sire_siblings_momentum_source, \
    horse_name_to_subject_id_source, average_place_percentile_source, average_relative_distance_behind_source, \
    dam_siblings_momentum_source, sire_and_dam_siblings_momentum_source, \
    dam_sire_siblings_momentum_source


class SireSiblingsMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = sire_siblings_momentum_source.get_attribute_group_key(race_card, horse, ["sire", "age"])
        sire_siblings_momentum = sire_siblings_momentum_source.get_average_of_name(key)

        if sire_siblings_momentum == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_siblings_momentum


class DamSiblingsMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = dam_siblings_momentum_source.get_attribute_group_key(race_card, horse, ["dam", "age"])
        dam_siblings_momentum = dam_siblings_momentum_source.get_average_of_name(key)

        if dam_siblings_momentum == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_siblings_momentum


class SireAndDamSiblingsMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = sire_and_dam_siblings_momentum_source.get_attribute_group_key(race_card, horse, ["sire", "dam", "age"])
        sire_and_dam_siblings_momentum = sire_and_dam_siblings_momentum_source.get_average_of_name(key)

        if sire_and_dam_siblings_momentum == -1:
            return self.PLACEHOLDER_VALUE

        return sire_and_dam_siblings_momentum


class DamSireSiblingsMomentum(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = dam_sire_siblings_momentum_source.get_attribute_group_key(race_card, horse, ["dam_sire", "age"])
        dam_sire_siblings_momentum = dam_sire_siblings_momentum_source.get_average_of_name(key)

        if dam_sire_siblings_momentum == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam_sire) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_sire_siblings_momentum
