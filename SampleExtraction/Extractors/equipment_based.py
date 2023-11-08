from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.feature_sources.feature_sources import equipment_already_worn_source


class HasFirstTimeEquipment(FeatureExtractor):

    def __init__(self, equipment_code: str):
        super().__init__()
        self.equipment_code = equipment_code

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        already_worn_equipment = equipment_already_worn_source.get_previous_of_name(str(horse.subject_id))

        if self.equipment_code not in already_worn_equipment and self.equipment_code in horse.equipments:
            return 1

        return 0


class HasFirstTimeBlinkers(HasFirstTimeEquipment):

    def __init__(self):
        super().__init__("b")


class HasFirstTimeVisor(HasFirstTimeEquipment):

    def __init__(self):
        super().__init__("v")


class HasFirstTimeHood(HasFirstTimeEquipment):

    def __init__(self):
        super().__init__("h")


class HasFirstTimeCheekPieces(HasFirstTimeEquipment):

    def __init__(self):
        super().__init__("s")


class HasBlinkers(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("b" in horse.equipments)


class HasVisor(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("v" in horse.equipments)


class HasHood(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("h" in horse.equipments)


class HasCheekPieces(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("s" in horse.equipments)


class HasEyeCovers(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("ec" in horse.equipments)


class HasEyeShield(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("es" in horse.equipments)


class HasTongueStrap(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return int("t" in horse.equipments)
