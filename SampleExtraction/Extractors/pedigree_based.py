from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.feature_sources import average_relative_distance_behind_source, \
    horse_name_to_subject_id_source, average_place_percentile_source, sire_siblings_place_percentile_source, \
    dam_siblings_place_percentile_source, sire_and_dam_siblings_place_percentile_source, \
    dam_sire_siblings_place_percentile_source


class SireSiblingsPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_siblings_place_percentile = sire_siblings_place_percentile_source.get_average_of_name(horse.sire)

        if sire_siblings_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_siblings_place_percentile


class SirePlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_place_percentile = average_place_percentile_source.get_average_of_name(horse.sire)

        if sire_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_place_percentile


class SireRelativeDistanceBehind(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        sire_relative_distance_behind = average_relative_distance_behind_source.get_average_of_name(horse.sire)

        if sire_relative_distance_behind == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.sire) > 1:
            return self.PLACEHOLDER_VALUE

        return sire_relative_distance_behind

class DamSiblingsPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_siblings_place_percentile = dam_siblings_place_percentile_source.get_average_of_name(horse.dam)

        if dam_siblings_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_siblings_place_percentile


class SireAndDamSiblingsPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        key = sire_and_dam_siblings_place_percentile_source.get_attribute_group_key(race_card, horse, ["sire", "dam"])
        sire_and_dam_sibling_place_percentile = sire_and_dam_siblings_place_percentile_source.get_average_of_name(key)

        if sire_and_dam_sibling_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        return sire_and_dam_sibling_place_percentile


class DamSireSiblingsPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_sire_siblings_place_percentile = dam_sire_siblings_place_percentile_source.get_average_of_name(horse.dam_sire)

        if dam_sire_siblings_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam_sire) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_sire_siblings_place_percentile


class DamPlacePercentile(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_place_percentile = average_place_percentile_source.get_average_of_name(horse.dam)

        if dam_place_percentile == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_place_percentile


class DamRelativeDistanceBehind(FeatureExtractor):

    PLACEHOLDER_VALUE = -1

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        dam_relative_distance_behind = average_relative_distance_behind_source.get_average_of_name(horse.dam)

        if dam_relative_distance_behind == -1:
            return self.PLACEHOLDER_VALUE

        if horse_name_to_subject_id_source.get_n_ids_of_horse_name(horse.dam) > 1:
            return self.PLACEHOLDER_VALUE

        return dam_relative_distance_behind
