import json
import pickle

from numpy import ndarray

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors import feature_sources
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.feature_sources import previous_track_name_source
from util.category_encoder import get_category_encoding


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
        return get_category_encoding("surface", str(race_card.surface))


class CurrentRaceType(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_type", str(race_card.race_type))


class CurrentRaceTypeDetail(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_type_detail", str(race_card.race_type_detail))


class CurrentRaceClass(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return int(race_card.race_class)


class CurrentRaceCategory(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return get_category_encoding("race_category", str(race_card.category))


class CurrentGoing(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.is_categorical = True

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        return get_category_encoding("going", str(race_card.going))


class WeightAdvantage(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        horse_weight = horse.jockey.weight
        if horse_weight in [-1, 0]:
            return -1
        return race_card.mean_horse_weight / horse_weight


class AgeFrom(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.age_from


class AgeTo(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        return race_card.age_to


class HasTrainerMultipleHorses(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> int:
        trainer_names = [
            other_horse.trainer_name for other_horse in race_card.horses if other_horse.trainer_name == horse.trainer_name
        ]

        return int(len(trainer_names) > 1)


class DrawBias(FeatureExtractor):

    def __init__(self):
        super().__init__()

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        draw_bias = feature_sources.draw_bias_source.get_draw_bias(race_card.track_name, horse.post_position)
        if draw_bias == -1:
            return self.PLACEHOLDER_VALUE
        return draw_bias / 20


unknown_location_list = []


class TravelDistance(FeatureExtractor):

    previous_track_name_source.previous_value_attribute_groups.append(["subject_id"])

    def __init__(self):
        super().__init__()
        with open("../data/locations.json", "r") as f:
            self.locations = json.load(f)
        self.beeline_distances: ndarray = pickle.load(open("../data/beeline_distances.bin", "rb"))

    def get_value(self, race_card: RaceCard, horse: Horse) -> float:
        previous_track_name = previous_track_name_source.get_previous_of_name(str(horse.subject_id))

        if previous_track_name is None:
            return self.PLACEHOLDER_VALUE

        if previous_track_name not in self.locations:
            if previous_track_name not in unknown_location_list:
                unknown_location_list.append(previous_track_name)
                print(unknown_location_list)
            return self.PLACEHOLDER_VALUE

        location_id_current = self.locations[race_card.track_name]["location_id"]
        location_id_previous = self.locations[previous_track_name]["location_id"]

        travel_distance = self.beeline_distances[location_id_current][location_id_previous]

        return travel_distance / 1000


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
