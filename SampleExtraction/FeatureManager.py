from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor, FeatureSourceExtractor, LayoffExtractor
from SampleExtraction.Extractors.current_race_based import CurrentRaceTrack, CurrentRaceClass, CurrentRaceSurface, \
    CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceCategory, CurrentGoing, CurrentDistance, CurrentPurse, TravelDistance
from SampleExtraction.Extractors.horse_attributes_based import CurrentRating, Age, Gender, TrainerChangeEarningsRateDiff
from SampleExtraction.Extractors.jockey_based import CurrentJockeyWeight, WeightAllowance, OutOfHandicapWeight
from SampleExtraction.feature_sources.feature_sources import PreviousValueSource, MaxValueSource, AverageValueSource, \
    TrackVariantSource, FeatureValueGroup
from SampleExtraction.feature_sources.value_calculators import win_probability, momentum, place_percentile, \
    race_distance, \
    race_going, race_class, relative_distance_behind, has_pulled_up, adjusted_race_distance, weight


class FeatureManager:

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features

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

        self.avg_window_3_min_obs_1_source = AverageValueSource(window_size=3, min_obs_thresh=1)

        self.avg_window_3_min_obs_3_source = AverageValueSource(window_size=3, min_obs_thresh=3)
        self.avg_window_5_min_obs_3_source = AverageValueSource(window_size=5, min_obs_thresh=3)
        self.avg_window_7_min_obs_3_source = AverageValueSource(window_size=7, min_obs_thresh=3)

        self.avg_window_3_min_obs_10_source = AverageValueSource(window_size=3, min_obs_thresh=10)
        self.avg_window_5_min_obs_10_source = AverageValueSource(window_size=5, min_obs_thresh=10)
        self.avg_window_7_min_obs_10_source = AverageValueSource(window_size=7, min_obs_thresh=10)

        self.avg_window_30_min_obs_10_source = AverageValueSource(window_size=30, min_obs_thresh=10)
        self.avg_window_50_min_obs_10_source = AverageValueSource(window_size=50, min_obs_thresh=10)

        self.track_variant_source: TrackVariantSource = TrackVariantSource()

        self.feature_sources = [
            self.previous_value_source,
            self.max_value_source,

            self.avg_window_3_min_obs_1_source,

            self.avg_window_3_min_obs_3_source,
            self.avg_window_5_min_obs_3_source,
            self.avg_window_7_min_obs_3_source,

            self.avg_window_3_min_obs_10_source,
            self.avg_window_5_min_obs_10_source,
            self.avg_window_7_min_obs_10_source,

            self.avg_window_30_min_obs_10_source,
            self.avg_window_50_min_obs_10_source,

            self.track_variant_source
        ]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        self.feature_names = [feature.get_name() for feature in self.features]
        self.selected_features = self.features
        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        horse_win_prob = FeatureValueGroup(["subject_id"], win_probability)

        horse_surface_win_prob = FeatureValueGroup(["subject_id", "surface"], win_probability)
        horse_track_win_prob = FeatureValueGroup(["subject_id", "track_name"], win_probability)
        horse_class_win_prob = FeatureValueGroup(["subject_id", "race_class"], win_probability)

        horse_momentum = FeatureValueGroup(["subject_id"], momentum)

        horse_surface_momentum = FeatureValueGroup(["subject_id", "surface"], momentum)
        horse_track_momentum = FeatureValueGroup(["subject_id", "track_name"], momentum)
        horse_class_momentum = FeatureValueGroup(["subject_id", "race_class"], momentum)

        horse_place_percentile = FeatureValueGroup(["subject_id"], place_percentile)

        horse_surface_place_percentile = FeatureValueGroup(["subject_id", "surface"], place_percentile)
        horse_track_place_percentile = FeatureValueGroup(["subject_id", "track_name"], place_percentile)
        horse_class_place_percentile = FeatureValueGroup(["subject_id", "race_class"], place_percentile)

        horse_relative_distance_behind = FeatureValueGroup(["subject_id"], relative_distance_behind)

        horse_surface_relative_distance_behind = FeatureValueGroup(["subject_id", "surface"], relative_distance_behind)
        horse_track_relative_distance_behind = FeatureValueGroup(["subject_id", "track_name"], relative_distance_behind)
        horse_class_relative_distance_behind = FeatureValueGroup(["subject_id", "race_class"], relative_distance_behind)

        horse_weight = FeatureValueGroup(["subject_id"], weight)

        horse_has_pulled_up = FeatureValueGroup(["subject_id"], has_pulled_up)

        horse_race_adjusted_distance = FeatureValueGroup(["subject_id"], adjusted_race_distance)
        horse_race_going = FeatureValueGroup(["subject_id"], race_going)
        horse_race_class = FeatureValueGroup(["subject_id"], race_class)

        jockey_win_prob = FeatureValueGroup(["jockey_id"], win_probability)
        jockey_momentum = FeatureValueGroup(["jockey_id"], momentum)

        trainer_win_prob = FeatureValueGroup(["trainer_id"], win_probability)
        trainer_momentum = FeatureValueGroup(["trainer_id"], momentum)

        trainer_class_momentum = FeatureValueGroup(["trainer_id", "race_class"], momentum)

        breeder_win_prob = FeatureValueGroup(["breeder"], win_probability)
        breeder_momentum = FeatureValueGroup(["breeder"], momentum)

        owner_win_prob = FeatureValueGroup(["owner"], win_probability)
        owner_momentum = FeatureValueGroup(["owner"], momentum)

        prev_value_features = [
            FeatureSourceExtractor(self.previous_value_source, horse_win_prob),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_track_win_prob),
            FeatureSourceExtractor(self.previous_value_source, horse_class_win_prob),

            FeatureSourceExtractor(self.previous_value_source, horse_momentum),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_momentum),
            FeatureSourceExtractor(self.previous_value_source, horse_track_momentum),
            FeatureSourceExtractor(self.previous_value_source, horse_class_momentum),

            FeatureSourceExtractor(self.previous_value_source, horse_place_percentile),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_place_percentile),
            FeatureSourceExtractor(self.previous_value_source, horse_track_place_percentile),
            FeatureSourceExtractor(self.previous_value_source, horse_class_place_percentile),

            FeatureSourceExtractor(self.previous_value_source, horse_relative_distance_behind),

            FeatureSourceExtractor(self.previous_value_source, horse_surface_relative_distance_behind),
            FeatureSourceExtractor(self.previous_value_source, horse_track_relative_distance_behind),
            FeatureSourceExtractor(self.previous_value_source, horse_class_relative_distance_behind),

            FeatureSourceExtractor(self.previous_value_source, horse_race_adjusted_distance),
            FeatureSourceExtractor(self.previous_value_source, horse_race_going),
            FeatureSourceExtractor(self.previous_value_source, horse_race_class),

            # FeatureSourceExtractor(previous_value_source, horse_has_pulled_up),

            TravelDistance(self.previous_value_source),

            TrainerChangeEarningsRateDiff(self.previous_value_source, self.avg_window_50_min_obs_10_source, trainer_class_momentum)
        ]

        max_value_features = [
            FeatureSourceExtractor(self.max_value_source, horse_win_prob),

            FeatureSourceExtractor(self.max_value_source, horse_surface_win_prob),
            FeatureSourceExtractor(self.max_value_source, horse_track_win_prob),
            FeatureSourceExtractor(self.max_value_source, horse_class_win_prob),

            FeatureSourceExtractor(self.max_value_source, horse_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_surface_momentum),
            FeatureSourceExtractor(self.max_value_source, horse_track_momentum),
            FeatureSourceExtractor(self.max_value_source, horse_class_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_place_percentile),

            FeatureSourceExtractor(self.max_value_source, horse_surface_place_percentile),
            FeatureSourceExtractor(self.max_value_source, horse_track_place_percentile),
            FeatureSourceExtractor(self.max_value_source, horse_class_place_percentile),

            FeatureSourceExtractor(self.max_value_source, jockey_win_prob),
            FeatureSourceExtractor(self.max_value_source, jockey_momentum),

            FeatureSourceExtractor(self.max_value_source, trainer_win_prob),
            FeatureSourceExtractor(self.max_value_source, trainer_momentum),

            FeatureSourceExtractor(self.max_value_source, horse_race_adjusted_distance),
            FeatureSourceExtractor(self.max_value_source, horse_weight)
        ]

        horse_name_momentum = FeatureValueGroup(["name"], momentum)
        dam_momentum = FeatureValueGroup(["dam"], momentum)
        sire_momentum = FeatureValueGroup(["sire"], momentum)

        avg_value_features = [
            FeatureSourceExtractor(self.avg_window_3_min_obs_3_source, horse_win_prob),
            FeatureSourceExtractor(self.avg_window_5_min_obs_3_source, horse_win_prob),
            FeatureSourceExtractor(self.avg_window_7_min_obs_3_source, horse_win_prob),

            FeatureSourceExtractor(self.avg_window_3_min_obs_3_source, horse_momentum),
            FeatureSourceExtractor(self.avg_window_5_min_obs_3_source, horse_momentum),
            FeatureSourceExtractor(self.avg_window_7_min_obs_3_source, horse_momentum),

            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, breeder_win_prob),
            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, breeder_momentum),

            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, owner_win_prob),
            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, owner_momentum),

            FeatureSourceExtractor(self.avg_window_50_min_obs_10_source, trainer_class_momentum),

            # TODO: Below are sibling features. These do not exclude the performance of the horse itself (it counts itself as a sibling)
            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, dam_momentum),
            FeatureSourceExtractor(self.avg_window_30_min_obs_10_source, sire_momentum),
        ]

        current_race_features = [
            CurrentRaceTrack(),
            CurrentRaceCategory(),
            CurrentDistance(),

            CurrentPurse(),

            Age(),
            Gender(),

            CurrentJockeyWeight(),
            WeightAllowance(),

            OutOfHandicapWeight(),
        ]

        layoff_features = [
            LayoffExtractor(self.previous_value_source, ["subject_id"]),
            LayoffExtractor(self.previous_value_source, ["subject_id", "track_name"]),
            LayoffExtractor(self.previous_value_source, ["subject_id", "race_class"]),
            LayoffExtractor(self.previous_value_source, ["subject_id", "surface"])
        ]

        return current_race_features + prev_value_features + max_value_features + avg_value_features + layoff_features

    @property
    def numerical_feature_names(self) -> List[str]:
        return [feature.get_name() for feature in self.selected_features if not feature.is_categorical]

    @property
    def categorical_feature_names(self) -> List[str]:
        return [feature.get_name() for feature in self.selected_features if feature.is_categorical]

    def set_features(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.__set_features_of_race_card(race_card)

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.features:
                feature_value = feature_extractor.get_value(race_card, horse)
                if self.__report_missing_features:
                    self.__report_if_feature_missing(horse, feature_extractor, feature_value)
                horse.set_feature_value(feature_extractor.get_name(), feature_value)

    def pre_update_feature_sources(self, race_card: RaceCard) -> None:
        if race_card.has_results:
            for feature_source in self.feature_sources:
                feature_source.pre_update(race_card)

    def post_update_feature_sources(self, race_cards: List[RaceCard]) -> None:
        for race_card in race_cards:
            if race_card.has_results and race_card.feature_source_validity:
                for feature_source in self.feature_sources:
                    feature_source.post_update(race_card)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
