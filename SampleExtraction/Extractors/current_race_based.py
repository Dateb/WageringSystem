from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse


class CurrentDistance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Distance"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.distance)


class CurrentRaceTrack(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Track"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(race_card.track_id)


class CurrentRaceSurface(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True
        self.surface_encoding = {
            "TRF": 0,
            "EQT": 1,
            "DRT": 2,
        }

    def get_name(self) -> str:
        return "Current_Race_Surface"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        surface = race_card.surface
        return self.surface_encoding[surface]


class CurrentRaceType(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True
        self.type_encoding = {
            "J": 0,
            "G": 1,
        }

    def get_name(self) -> str:
        return "Current_Race_Type"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        race_type = race_card.race_type
        return self.type_encoding[race_type]


class CurrentRaceTypeDetail(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True
        self.encoding_counter = 0
        self.type_detail_encoding = {}

    def get_name(self) -> str:
        return "Current_Race_Type_Detail"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not race_card.race_type_detail:
            return self.PLACEHOLDER_VALUE
        if race_card.race_type_detail not in self.type_detail_encoding:
            self.type_detail_encoding[race_card.race_type_detail] = self.encoding_counter
            self.encoding_counter += 1
        return self.type_detail_encoding[race_card.race_type_detail]


class CurrentRaceClass(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Class"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if race_card.race_class.isnumeric():
            return int(race_card.race_class)
        return self.PLACEHOLDER_VALUE


class CurrentRaceCategory(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True
        self.encoding_counter = 0
        self.category_encoding = {}

    def get_name(self) -> str:
        return "Current_Race_Category"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        if not race_card.category:
            return self.PLACEHOLDER_VALUE
        if race_card.category not in self.category_encoding:
            self.category_encoding[race_card.category] = self.encoding_counter
            self.encoding_counter += 1
        return self.category_encoding[race_card.category]


class CurrentGoing(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Current_Going"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return race_card.going


class HasTrainerMultipleHorses(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Has_Trainer_Multiple_Horses"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        trainer_names = [
            other_horse.trainer_name for other_horse in race_card.horses if other_horse.trainer_name == horse.trainer_name
        ]

        return int(len(trainer_names) > 1)
