import multiprocessing
import os
import time
from multiprocessing.pool import Pool
from threading import Thread
from typing import List, Tuple, Dict

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor, FeatureSourceExtractor, LayoffExtractor
from SampleExtraction.Extractors.current_race_based import CurrentRaceTrack, CurrentRaceClass, CurrentRaceSurface, \
    CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceCategory, CurrentEstimatedGoing, CurrentDistance, CurrentPurse, \
    TravelDistance, PlacesNum, HasTrainerMultipleHorses, HasPlaced, CurrentTemperature, CurrentWindSpeed, \
    CurrentHumidity
from SampleExtraction.Extractors.equipment_based import HasBlinkers, HasVisor, HasHood, HasCheekPieces, HasEyeCovers, \
    HasEyeShield, HasTongueStrap
from SampleExtraction.Extractors.horse_attributes_based import CurrentRating, Age, Gender, \
    TrainerChangeEarningsRateDiff, Origin
from SampleExtraction.Extractors.jockey_based import CurrentJockeyWeight, WeightAllowance, OutOfHandicapWeight
from SampleExtraction.Extractors.time_based import DayOfYearSin, DayOfYearCos, WeekDayCos, WeekDaySin, MinutesIntoDay
from SampleExtraction.feature_sources.feature_sources import PreviousValueSource, MaxValueSource, AverageValueSource, \
    TrackVariantSource, FeatureValueGroup, MinValueSource, CountSource, SumSource, \
    GoingSource, StreakSource, FeatureSource
from SampleExtraction.feature_sources.value_calculators import win_probability, momentum, \
    competitors_beaten, \
    race_distance, \
    race_class, relative_distance_behind, has_pulled_up, adjusted_race_distance, weight, one_constant, \
    has_won, purse, has_placed, place_percentile
from util.nested_dict import nested_dict
from util.stats_calculator import SimpleOnlineCalculator


class FeatureManager:

    def __init__(self, features: List[FeatureExtractor] = None):
        self.base_features = [
            # HasWon(),

            # IsFavorite(),
            # IndustryMarketWinProbabilityDiff(),
            #
            # BetfairOverround(),
            # IsSecondRaceForJockey(),

            # RacebetsWinProbability(),
            # BetfairPlaceMarketWinProbability(),

            # BaseTime(),
        ]

        self.previous_value_source = PreviousValueSource()

        self.max_value_source = MaxValueSource()
        self.min_value_source = MinValueSource()
        self.sum_source = SumSource()
        self.streak_source = StreakSource()

        self.avg_source_short_window = AverageValueSource(window_size=0.1)
        self.avg_source_medium_window = AverageValueSource(window_size=0.01)
        self.avg_source_long_window = AverageValueSource(window_size=0.001)

        self.track_variant_source: TrackVariantSource = TrackVariantSource()
        self.going_source: GoingSource = GoingSource()

        self.feature_sources = [
            self.previous_value_source,

            self.max_value_source,
            self.min_value_source,
            self.sum_source,
            self.streak_source,

            self.avg_source_short_window,
            self.avg_source_medium_window,
            self.avg_source_long_window,

            self.track_variant_source,
            self.going_source
        ]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        self.feature_names = [feature.name for feature in self.features]
        self.selected_features = self.features
        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        horse_win_prob = FeatureValueGroup(win_probability, ["subject_id"])

        horse_has_won = FeatureValueGroup(has_won, ["subject_id"])
        horse_race_type_has_won = FeatureValueGroup(has_won, ["subject_id"], ["race_type"])

        horse_has_placed = FeatureValueGroup(has_placed, ["subject_id"])

        # horse_distance_category_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["distance_category"])

        horse_surface_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["surface"])
        horse_weather_type_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["weather_type"])

        horse_surface_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"], ["surface"])
        horse_surface_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"], ["surface"])

        horse_surface_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id"],
                                                                   ["surface"])
        horse_surface_momentum = FeatureValueGroup(momentum, ["subject_id"], ["surface"])

        horse_race_type_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["race_type"])

        horse_race_type_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"], ["race_type"])
        horse_race_type_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"], ["race_type"])

        horse_race_type_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id"],
                                                                     ["race_type"])
        horse_race_type_momentum = FeatureValueGroup(momentum, ["subject_id"], ["race_type"])

        horse_category_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["category"])
        horse_category_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"], ["category"])
        horse_category_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"], ["category"])

        horse_track_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["track_name"])
        horse_class_win_prob = FeatureValueGroup(win_probability, ["subject_id"], ["race_class"])

        horse_momentum = FeatureValueGroup(momentum, ["subject_id"])

        horse_track_momentum = FeatureValueGroup(momentum, ["subject_id"], ["track_name"])
        horse_class_momentum = FeatureValueGroup(momentum, ["subject_id"], ["race_class"])

        horse_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"])
        horse_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"])

        horse_track_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"], ["track_name"])
        horse_track_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"], ["track_name"])
        horse_class_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id"], ["race_class"])
        horse_class_place_percentile = FeatureValueGroup(place_percentile, ["subject_id"], ["race_class"])

        horse_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id"])

        horse_track_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id"],
                                                                 ["track_name"])
        horse_class_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id"],
                                                                 ["race_class"])

        horse_weight = FeatureValueGroup(weight, ["subject_id"])

        horse_race_adjusted_distance = FeatureValueGroup(adjusted_race_distance, ["subject_id"])
        horse_race_class = FeatureValueGroup(race_class, ["subject_id"])

        jockey_win_prob = FeatureValueGroup(win_probability, ["jockey_id"])
        jockey_momentum = FeatureValueGroup(momentum, ["jockey_id"])

        jockey_weather_type_win_prob = FeatureValueGroup(win_probability, ["jockey_id"], ["weather_type"])
        jockey_race_type_win_prob = FeatureValueGroup(win_probability, ["jockey_id"], ["race_type"])
        jockey_race_type_competitors_beaten = FeatureValueGroup(competitors_beaten, ["jockey_id"], ["race_type"])
        jockey_race_type_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["jockey_id"],
                                                                      ["race_type"])

        jockey_going_win_prob = FeatureValueGroup(win_probability, ["jockey_id"], ["estimated_going"])
        jockey_going_competitors_beaten = FeatureValueGroup(competitors_beaten, ["jockey_id"], ["estimated_going"])

        trainer_weather_type_win_prob = FeatureValueGroup(win_probability, ["trainer_id"], ["weather_type"])
        trainer_race_type_win_prob = FeatureValueGroup(win_probability, ["trainer_id"], ["race_type"])
        trainer_race_type_competitors_beaten = FeatureValueGroup(competitors_beaten, ["trainer_id"], ["race_type"])
        trainer_race_type_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["trainer_id"],
                                                                       ["race_type"])

        trainer_going_win_prob = FeatureValueGroup(win_probability, ["trainer_id"], ["estimated_going"])
        trainer_going_competitors_beaten = FeatureValueGroup(competitors_beaten, ["trainer_id"], ["estimated_going"])

        owner_race_type_win_prob = FeatureValueGroup(win_probability, ["owner"], ["race_type"])
        owner_race_type_competitors_beaten = FeatureValueGroup(competitors_beaten, ["owner"], ["race_type"])
        owner_race_type_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["owner"], ["race_type"])

        trainer_win_prob = FeatureValueGroup(win_probability, ["trainer_id"])
        trainer_momentum = FeatureValueGroup(momentum, ["trainer_id"])

        jockey_class_win_probability = FeatureValueGroup(win_probability, ["jockey_id"], ["race_class"])
        jockey_surface_win_probability = FeatureValueGroup(win_probability, ["jockey_id"], ["surface"])

        trainer_class_win_probability = FeatureValueGroup(win_probability, ["trainer_id"], ["race_class"])
        trainer_surface_win_probability = FeatureValueGroup(win_probability, ["trainer_id"], ["surface"])

        jockey_class_competitors_beaten = FeatureValueGroup(competitors_beaten, ["jockey_id"], ["race_class"])
        trainer_class_competitors_beaten = FeatureValueGroup(competitors_beaten, ["trainer_id"], ["race_class"])

        jockey_class_momentum = FeatureValueGroup(momentum, ["jockey_id"], ["race_class"])
        trainer_class_momentum = FeatureValueGroup(momentum, ["trainer_id"], ["race_class"])

        breeder_win_prob = FeatureValueGroup(win_probability, ["breeder"])
        breeder_momentum = FeatureValueGroup(momentum, ["breeder"])

        owner_win_prob = FeatureValueGroup(win_probability, ["owner"])
        owner_momentum = FeatureValueGroup(momentum, ["owner"])

        dam_win_probability = FeatureValueGroup(win_probability, ["dam", "age"])
        dam_competitors_beaten = FeatureValueGroup(competitors_beaten, ["dam", "age"])
        dam_momentum = FeatureValueGroup(momentum, ["dam", "age"])

        sire_win_probability = FeatureValueGroup(win_probability, ["sire", "age"])

        jockey_track_win_probability = FeatureValueGroup(win_probability, ["jockey_id"], ["track_name"])
        trainer_track_win_probability = FeatureValueGroup(win_probability, ["trainer_id"], ["track_name"])
        owner_track_win_probability = FeatureValueGroup(win_probability, ["owner"], ["track_name"])

        horse_jockey_win_probability = FeatureValueGroup(win_probability, ["subject_id", "jockey_id"])
        horse_jockey_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id", "jockey_id"])
        horse_jockey_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id", "jockey_id"])
        horse_jockey_momentum = FeatureValueGroup(momentum, ["subject_id", "jockey_id"])

        horse_trainer_win_probability = FeatureValueGroup(win_probability, ["subject_id", "trainer_id"])
        horse_trainer_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id", "trainer_id"])
        horse_trainer_relative_distance_behind = FeatureValueGroup(relative_distance_behind,
                                                                   ["subject_id", "trainer_id"])
        horse_trainer_momentum = FeatureValueGroup(momentum, ["subject_id", "trainer_id"])

        horse_owner_win_probability = FeatureValueGroup(win_probability, ["subject_id", "owner"])
        horse_owner_competitors_beaten = FeatureValueGroup(competitors_beaten, ["subject_id", "owner"])
        horse_owner_relative_distance_behind = FeatureValueGroup(relative_distance_behind, ["subject_id", "owner"])
        horse_owner_momentum = FeatureValueGroup(momentum, ["subject_id", "owner"])

        jockey_trainer_win_probability = FeatureValueGroup(win_probability, ["jockey_id", "trainer_id"])
        jockey_trainer_competitors_beaten = FeatureValueGroup(competitors_beaten, ["jockey_id", "trainer_id"])
        jockey_trainer_relative_distance_behind = FeatureValueGroup(relative_distance_behind,
                                                                    ["jockey_id", "trainer_id"])
        jockey_trainer_momentum = FeatureValueGroup(momentum, ["jockey_id", "trainer_id"])

        horse_purse = FeatureValueGroup(purse, ["subject_id"])
        jockey_purse = FeatureValueGroup(purse, ["jockey_id"])
        trainer_purse = FeatureValueGroup(purse, ["trainer_id"])

        prev_value_features = [
            FeatureSourceExtractor(self.previous_value_source, horse_has_placed),

            FeatureSourceExtractor(self.previous_value_source, horse_win_prob),

            # FeatureSourceExtractor(self.previous_value_source, horse_distance_category_win_prob),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_track_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_class_win_prob),

            FeatureSourceExtractor(self.previous_value_source, horse_category_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_category_competitors_beaten),

            FeatureSourceExtractor(self.previous_value_source, horse_momentum),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_momentum),
            FeatureSourceExtractor(self.previous_value_source, horse_track_momentum),
            FeatureSourceExtractor(self.previous_value_source, horse_class_momentum),

            FeatureSourceExtractor(self.previous_value_source, horse_competitors_beaten),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_competitors_beaten),
            FeatureSourceExtractor(self.previous_value_source, horse_track_competitors_beaten),
            FeatureSourceExtractor(self.previous_value_source, horse_class_competitors_beaten),

            FeatureSourceExtractor(self.previous_value_source, horse_relative_distance_behind),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_relative_distance_behind),
            FeatureSourceExtractor(self.previous_value_source, horse_track_relative_distance_behind),
            FeatureSourceExtractor(self.previous_value_source, horse_class_relative_distance_behind),

            FeatureSourceExtractor(self.previous_value_source, horse_race_adjusted_distance),
            FeatureSourceExtractor(self.previous_value_source, horse_race_class),

            FeatureSourceExtractor(self.previous_value_source, horse_race_type_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_race_type_competitors_beaten),
            FeatureSourceExtractor(self.previous_value_source, horse_race_type_momentum),

            TravelDistance(self.previous_value_source),
        ]

        max_value_features = [
            FeatureSourceExtractor(self.max_value_source, horse_win_prob),

            FeatureSourceExtractor(self.max_value_source, horse_surface_win_prob),
            FeatureSourceExtractor(self.max_value_source, horse_class_win_prob),

            FeatureSourceExtractor(self.max_value_source, horse_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_surface_momentum),
            FeatureSourceExtractor(self.max_value_source, horse_track_momentum),
            FeatureSourceExtractor(self.max_value_source, horse_class_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_competitors_beaten),

            FeatureSourceExtractor(self.max_value_source, horse_surface_competitors_beaten),
            FeatureSourceExtractor(self.max_value_source, horse_class_competitors_beaten),

            FeatureSourceExtractor(self.max_value_source, jockey_win_prob),
            FeatureSourceExtractor(self.max_value_source, jockey_momentum),

            FeatureSourceExtractor(self.max_value_source, trainer_win_prob),
            FeatureSourceExtractor(self.max_value_source, trainer_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_race_adjusted_distance),
            FeatureSourceExtractor(self.max_value_source, horse_weight),

            FeatureSourceExtractor(self.max_value_source, dam_win_probability),
            FeatureSourceExtractor(self.max_value_source, dam_competitors_beaten),
            FeatureSourceExtractor(self.max_value_source, dam_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_purse),
            FeatureSourceExtractor(self.max_value_source, jockey_purse),
            FeatureSourceExtractor(self.max_value_source, trainer_purse),
        ]

        min_value_features = [
            FeatureSourceExtractor(self.min_value_source, horse_race_adjusted_distance),
            FeatureSourceExtractor(self.min_value_source, horse_weight)
        ]

        avg_value_features = [
            FeatureSourceExtractor(self.avg_source_medium_window, horse_win_prob),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_has_won),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_race_type_has_won),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_category_win_prob),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_category_competitors_beaten),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_class_win_prob),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_class_competitors_beaten),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_class_relative_distance_behind),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_class_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_race_type_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_race_type_relative_distance_behind),

            FeatureSourceExtractor(self.avg_source_medium_window, breeder_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, breeder_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, owner_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, owner_momentum),

            # FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, jockey_weather_type_win_prob),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_race_type_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_race_type_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_race_type_relative_distance_behind),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_going_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_going_competitors_beaten),

            # FeatureSourceExtractor(self.avg_window_50_min_obs_10_source, trainer_weather_type_win_prob),

            FeatureSourceExtractor(self.avg_source_medium_window, trainer_race_type_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_race_type_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_race_type_relative_distance_behind),

            FeatureSourceExtractor(self.avg_source_medium_window, trainer_going_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_going_competitors_beaten),

            FeatureSourceExtractor(self.avg_source_medium_window, owner_race_type_win_prob),
            FeatureSourceExtractor(self.avg_source_medium_window, owner_race_type_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, owner_race_type_relative_distance_behind),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_class_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_surface_win_probability),

            FeatureSourceExtractor(self.avg_source_medium_window, trainer_class_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_surface_win_probability),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_class_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_class_competitors_beaten),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_class_momentum),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_class_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, dam_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, dam_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, dam_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, sire_win_probability),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_track_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, trainer_track_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, owner_track_win_probability),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_jockey_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_jockey_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_jockey_relative_distance_behind),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_jockey_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_trainer_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_trainer_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_trainer_relative_distance_behind),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_trainer_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, horse_owner_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_owner_relative_distance_behind),
            FeatureSourceExtractor(self.avg_source_medium_window, horse_owner_momentum),

            FeatureSourceExtractor(self.avg_source_medium_window, jockey_trainer_win_probability),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_trainer_competitors_beaten),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_trainer_relative_distance_behind),
            FeatureSourceExtractor(self.avg_source_medium_window, jockey_trainer_momentum)
        ]

        horse_one_constant = FeatureValueGroup(one_constant, ["subject_id"])
        horse_race_class_one_constant = FeatureValueGroup(one_constant, ["subject_id"], ["race_class"])

        jockey_one_constant = FeatureValueGroup(one_constant, ["jockey_id"])
        trainer_one_constant = FeatureValueGroup(one_constant, ["trainer_id"])

        sum_features = [
            FeatureSourceExtractor(self.sum_source, horse_one_constant),
            FeatureSourceExtractor(self.sum_source, horse_race_class_one_constant),

            FeatureSourceExtractor(self.sum_source, jockey_one_constant),
            FeatureSourceExtractor(self.sum_source, trainer_one_constant),

            FeatureSourceExtractor(self.sum_source, horse_purse),
            FeatureSourceExtractor(self.sum_source, jockey_purse),
            FeatureSourceExtractor(self.sum_source, trainer_purse),
        ]

        current_race_features = [
            CurrentRaceCategory(),
            CurrentEstimatedGoing(),
            # CurrentTemperature(),
            # CurrentWindSpeed(),
            # CurrentHumidity(),

            HasVisor(),

            HasTrainerMultipleHorses(),

            Age(),
            Gender(),
            Origin(),

            CurrentJockeyWeight(),
        ]

        layoff_features = [
            LayoffExtractor(self.previous_value_source, ["subject_id"], []),
            # LayoffExtractor(self.previous_value_source, ["subject_id"], ["distance_category"]),
            LayoffExtractor(self.previous_value_source, ["subject_id", "jockey_id"], []),
            LayoffExtractor(self.previous_value_source, ["subject_id"], ["track_name"]),
            LayoffExtractor(self.previous_value_source, ["subject_id"], ["race_class"]),
            LayoffExtractor(self.previous_value_source, ["subject_id"], ["surface"]),
        ]

        streak_features = [
            FeatureSourceExtractor(self.streak_source, horse_has_won),
            FeatureSourceExtractor(self.streak_source, horse_has_placed)
        ]

        self.feature_value_groups = []
        for feature_source in self.feature_sources:
            for feature_value_group in feature_source.feature_value_groups:
                if feature_value_group not in self.feature_value_groups:
                    self.feature_value_groups.append(feature_value_group)

        self.feature_value_group_to_source_map = {feature_value_group: [] for feature_value_group in
                                                  self.feature_value_groups}
        for feature_source in self.feature_sources:
            for feature_value_group in feature_source.feature_value_groups:
                self.feature_value_group_to_source_map[feature_value_group].append(feature_source)

        return (
                current_race_features + prev_value_features
                + max_value_features + min_value_features +
                avg_value_features + sum_features + layoff_features + streak_features
        )

    @property
    def numerical_feature_names(self) -> List[str]:
        return [feature.name for feature in self.selected_features if not feature.is_categorical]

    @property
    def categorical_feature_names(self) -> List[str]:
        return [feature.name for feature in self.selected_features if feature.is_categorical]

    def set_features(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.__set_features_of_race_card(race_card)

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.features:
                feature_value = feature_extractor.get_value(race_card, horse)
                horse.set_feature_value(feature_extractor.name, feature_value)

    def pre_update_feature_sources(self, race_card: RaceCard) -> None:
        for feature_source in self.feature_sources:
            feature_source.pre_update(race_card)

    def post_update_feature_sources(self, race_cards: List[RaceCard]) -> None:
        race_cards = [race_card for race_card in race_cards if
                      race_card.has_results and race_card.feature_source_validity]

        current_date = None
        for feature_value_group in self.feature_value_groups:
            feature_values = nested_dict()
            for race_card in race_cards:
                current_date = race_card.date
                if race_card.is_valid_sample:
                    race_card_key = feature_value_group.race_card_key_cache[race_card.race_id]
                else:
                    race_card_key = feature_value_group.get_race_card_key(race_card)
                for horse in race_card.horses:
                    if not horse.is_scratched:
                        if race_card.is_valid_sample:
                            feature_value_group_key = feature_value_group.key_cache[horse.subject_id]
                        else:
                            feature_value_group_key = feature_value_group.get_key(race_card_key, horse)
                        new_feature_value = feature_value_group.value_calculator(race_card, horse)
                        if new_feature_value is not None:
                            if isinstance(new_feature_value, float):
                                if feature_value_group_key not in feature_values:
                                    feature_values[feature_value_group_key]["count"] = 1
                                    feature_values[feature_value_group_key]["avg"] = new_feature_value
                                else:
                                    feature_values[feature_value_group_key]["count"] += 1
                                    feature_values[feature_value_group_key]["avg"] = SimpleOnlineCalculator().calculate_average(
                                        old_average=feature_values[feature_value_group_key]["avg"],
                                        new_obs=new_feature_value,
                                        n_days_since_last_obs=0,
                                        count=feature_values[feature_value_group_key]["count"]
                                    )
                            else:
                                feature_values[feature_value_group_key]["avg"] = new_feature_value

            for feature_source in self.feature_value_group_to_source_map[feature_value_group]:
                feature_source.post_update(race_cards, feature_values, current_date)

        for feature_value_group in self.feature_value_groups:
            feature_value_group.clear_cache()
