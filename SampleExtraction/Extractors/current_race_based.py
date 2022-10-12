from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors import feature_sources
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from util.category_encoder import get_category_encoding


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
        return get_category_encoding("track_name", str(race_card.track_name))


class CurrentRaceSurface(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Surface"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("surface", str(race_card.surface))


class CurrentRaceType(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Type"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_type", str(race_card.race_type))


class CurrentRaceTypeDetail(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Type_Detail"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_type_detail", str(race_card.race_type_detail))


class CurrentRaceClass(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Class"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_class", str(race_card.race_class))


class CurrentRaceCategory(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Race_Category"

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_category", str(race_card.category))


class CurrentGoing(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_name(self) -> str:
        return "Current_Going"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_category_encoding("going", str(race_card.going))


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


class DrawBias(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_name(self) -> str:
        return "Draw_Bias"

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        draw_bias = feature_sources.draw_bias_source.draw_bias(race_card.track_name, horse.post_position)
        if draw_bias == -1:
            return self.PLACEHOLDER_VALUE
        return draw_bias
