import json
import pickle

from numpy import ndarray

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.feature_sources.feature_sources import FeatureValueGroup, PreviousValueSource
from SampleExtraction.feature_sources.value_calculators import get_track_name
from util.category_encoder import get_category_encoding


class HasPlaced(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(horse.has_placed)


class CurrentPurse(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.purse


class CurrentHorseCount(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.n_horses


class CurrentDistance(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.distance)


class PlacesNum(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.places_num)


class CurrentRaceTrack(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return race_card.track_name


class CurrentRaceSurface(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.surface


class CurrentRaceType(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return race_card.race_type


class CurrentRaceTypeDetail(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return race_card.race_type_detail


class CurrentRaceClass(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return race_card.race_class


class CurrentRaceCategory(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> str:
        return str(race_card.category)


class CurrentEstimatedGoing(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return float(race_card.estimated_going)


class WeightAdvantage(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        horse_weight = horse.jockey.weight
        if horse_weight in [-1, 0]:
            return -1
        return race_card.mean_horse_weight / horse_weight


class HasTrainerMultipleHorses(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        trainer_names = [
            other_horse.trainer.id for other_horse in race_card.horses if other_horse.trainer.id == horse.trainer.id
                                                                          and horse.trainer.id
        ]

        return int(len(trainer_names) > 1)


# class DrawBias(FeatureExtractor):
#
#     def __init__(self):
#         super().__init__()
#
#     def get_value(self, race_card: RaceCard, horse: Horse) -> float:
#         draw_bias = draw_bias_source.get_draw_bias(race_card.track_name, horse.post_position)
#         if draw_bias == -1:
#             return self.PLACEHOLDER_VALUE
#         return draw_bias


unknown_location_list = []


class TravelDistance(FeatureExtractor):

    def __init__(self, previous_value_source: PreviousValueSource):
        super().__init__()
        self.feature_source = previous_value_source

        self.feature_value_group = FeatureValueGroup(get_track_name, ["subject_id"])

        self.feature_source.register_feature_value_group(self.feature_value_group)

        with open("../data/locations.json", "r") as f:
            self.locations = json.load(f)
        self.beeline_distances: ndarray = pickle.load(open("../data/beeline_distances.bin", "rb"))

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_track_name = self.feature_source.get_feature_value(race_card, horse, self.feature_value_group)

        if previous_track_name is None:
            return self.PLACEHOLDER_VALUE

        if previous_track_name not in self.locations:
            if previous_track_name not in unknown_location_list:
                unknown_location_list.append(previous_track_name)
                print(unknown_location_list)
            return self.PLACEHOLDER_VALUE

        if race_card.track_name not in self.locations:
            print(f"Please add new unknown track location: {race_card.track_name}")
            return self.PLACEHOLDER_VALUE

        location_id_current = self.locations[race_card.track_name]["location_id"]
        location_id_previous = self.locations[previous_track_name]["location_id"]

        travel_distance = self.beeline_distances[location_id_current][location_id_previous]

        return travel_distance


class WeatherType(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE

        return get_category_encoding("weather_type", race_card.weather.weather_type)


class Temperature(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.temperature


class AirPressure(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.air_pressure


class Humidity(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.humidity


class WindSpeed(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.wind_speed


class WindDirection(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.wind_direction


class Cloudiness(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.cloudiness


class RainVolume(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        if race_card.weather is None:
            return self.PLACEHOLDER_VALUE
        return race_card.weather.rain_volume
