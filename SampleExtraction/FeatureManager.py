from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor, FeatureSourceExtractor, LayoffExtractor
from SampleExtraction.Extractors.current_race_based import CurrentRaceTrack, CurrentRaceClass, CurrentRaceSurface, \
    CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceCategory, CurrentGoing, CurrentDistance, CurrentPurse, AgeFrom, \
    AgeTo, TravelDistance
from SampleExtraction.Extractors.equipment_based import HasBlinkers, HasHood, HasCheekPieces, HasVisor, HasEyeCovers, \
    HasEyeShield
from SampleExtraction.Extractors.horse_attributes_based import CurrentRating, Age, Gender
from SampleExtraction.Extractors.jockey_based import CurrentJockeyWeight, WeightAllowance
from SampleExtraction.Extractors.time_based import MinutesIntoDay, MonthCos, MonthSin, DayOfMonthCos, DayOfMonthSin, \
    WeekDaySin, WeekDayCos
from SampleExtraction.feature_sources.feature_sources import PreviousValueSource, MaxValueSource, AverageValueSource, \
    TrackVariantSource, FeatureValueGroup
from SampleExtraction.feature_sources.value_calculators import win_probability, momentum, place_percentile, \
    race_distance, \
    race_going, race_class, relative_distance_behind, has_pulled_up


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

        self.avg_window_3_min_obs_1_source: AverageValueSource = AverageValueSource(window_size=3, min_obs_thresh=1)

        self.avg_window_3_min_obs_3_source: AverageValueSource = AverageValueSource(window_size=3, min_obs_thresh=3)
        self.avg_window_5_min_obs_3_source: AverageValueSource = AverageValueSource(window_size=5, min_obs_thresh=3)
        self.avg_window_7_min_obs_3_source: AverageValueSource = AverageValueSource(window_size=7, min_obs_thresh=3)

        self.avg_window_3_min_obs_10_source: AverageValueSource = AverageValueSource(window_size=3, min_obs_thresh=10)
        self.avg_window_5_min_obs_10_source: AverageValueSource = AverageValueSource(window_size=5, min_obs_thresh=10)
        self.avg_window_7_min_obs_10_source: AverageValueSource = AverageValueSource(window_size=7, min_obs_thresh=10)

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
        # window_sizes = [3, 5, 7]
        # win_prob_features = [HorseWinProbability(window_size=i) for i in window_sizes]
        # win_rate_features = [HorseWinRate(window_size=i) for i in window_sizes]
        # show_rate_features = [HorseShowRate(window_size=i) for i in window_sizes]
        # place_percentile_features = [HorsePlacePercentile(window_size=i) for i in window_sizes]
        # momentum_features = [HorseMomentum(window_size=i) for i in window_sizes]
        # window_time_length_features = [WindowTimeLength(window_size=i) for i in window_sizes]

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

        horse_has_pulled_up = FeatureValueGroup(["subject_id"], has_pulled_up)

        horse_distance = FeatureValueGroup(["subject_id"], race_distance)
        horse_going = FeatureValueGroup(["subject_id"], race_going)
        horse_race_class = FeatureValueGroup(["subject_id"], race_class)

        jockey_win_prob = FeatureValueGroup(["jockey_id"], win_probability)
        jockey_momentum = FeatureValueGroup(["jockey_id"], momentum)

        trainer_win_prob = FeatureValueGroup(["trainer_id"], win_probability)
        trainer_momentum = FeatureValueGroup(["trainer_id"], momentum)

        owner_win_prob = FeatureValueGroup(["owner"], win_probability)
        owner_momentum = FeatureValueGroup(["owner"], momentum)

        breeder_win_prob = FeatureValueGroup(["breeder"], win_probability)
        breeder_momentum = FeatureValueGroup(["breeder"], momentum)

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

            FeatureSourceExtractor(self.previous_value_source, horse_distance),
            FeatureSourceExtractor(self.previous_value_source, horse_going),
            FeatureSourceExtractor(self.previous_value_source, horse_race_class),

            # FeatureSourceExtractor(previous_value_source, horse_has_pulled_up),

            FeatureSourceExtractor(self.previous_value_source, jockey_win_prob),
            FeatureSourceExtractor(self.previous_value_source, jockey_momentum),

            FeatureSourceExtractor(self.previous_value_source, trainer_win_prob),
            FeatureSourceExtractor(self.previous_value_source, trainer_momentum),
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

            # FeatureSourceExtractor(avg_window_5_min_obs_3_source, horse_name_momentum, dam_momentum),
            # FeatureSourceExtractor(avg_window_5_min_obs_3_source, horse_name_momentum, sire_momentum),
        ]

        current_race_features = [
            CurrentRaceTrack(),
            CurrentRaceSurface(),

            CurrentRaceType(),
            CurrentRaceTypeDetail(),
            CurrentRaceCategory(),

            CurrentGoing(),
            CurrentDistance(),
            CurrentRaceClass(),

            CurrentPurse(),

            # TODO: Does not consider out of handicap horses (ratings are unfortunately already corrected)
            CurrentRating(),

            Age(),
            Gender(),

            AgeFrom(), AgeTo(),

            CurrentJockeyWeight(),
            WeightAllowance(),
        ]

        time_features = [
            MinutesIntoDay(),

            MonthCos(),
            MonthSin(),

            DayOfMonthCos(),
            DayOfMonthSin(),

            WeekDaySin(),
            WeekDayCos(),
        ]

        layoff_features = [
            LayoffExtractor(["subject_id"]),
            LayoffExtractor(["subject_id", "track_name"]),
            LayoffExtractor(["subject_id", "race_class"]),
            LayoffExtractor(["subject_id", "surface"])
        ]

        default_features = [

            # BetfairWinMarketWinProbability(),
            #
            # HorsePulledUpRate(),
            # PulledUpPreviousRace(),
            #
            # HorsePurseRate(),
            #
            #
            # HasPreviousRaces(),
            #
            # PreviousRaceLayoff(),
            #
            # SameTrackLayoff(),
            # SameClassLayoff(),
            # SameSurfaceLayoff(),
            #
            #
            #
            # WeightDifference(),
            # AllowanceDifference(),
            #
            # OwnerWinRateDifference(),
            #
            # DrawBias(),
            #
            #
            # HorseScratchedRate(),
            # JockeyScratchedRate(),
            # TrainerScratchedRate(),
            #
            # HasTrainerMultipleHorses(),
            #
            # SireSiblingsMomentum(),
            # DamSiblingsMomentum(),
            # SireAndDamSiblingsMomentum(),
            # DamSireSiblingsMomentum(),
            #
            #
            # BestClassPlace(),
            # LifeTimeStartCount(),
            #
            # DamMomentum(), SireMomentum(),
            #
            # HorseJockeyShowRate(),




            # PostPosition(),

            # DamPurseRate(), SirePurseRate(),

            # HasFirstTimeBlinkers(), HasFirstTimeVisor(), HasFirstTimeHood(), HasFirstTimeCheekPieces(),

            # DamPercentageBeaten(), SirePercentageBeaten(),

            # HighestLifetimeWinProbability(),

            # Needs improvement in regards with different start counts

            #
            # LifeTimeWinCount(),
            # LifeTimePlaceCount(),
            #

            #-----------------------------------------------------------------
            #Needs improvement:


            # HorseTopFinish()
            # MaxPastRatingExtractor(),

            # BestLifeTimeSpeedFigure(),

            # PreviousFasterThanFraction(),
            # PreviousSlowerThanFraction(),
            # JockeySurfaceWinRate(),
            # AveragePurse(),

            # Not tested:

            # TrainerClassWinRate(),
            # TrainerPercentageBeaten(),
            #
            # DamSirePurseRate(),
            # DamSirePercentageBeaten(),
            #
            # JockeyClassShowRate(),
            #
            # JockeyPurseRate(),
            # BreederPercentageBeaten(),
            #
            #
            #
            # BreederPurseRate(),
            # JockeyPercentageBeaten(),
            #
            # OwnerShowRate(),
            #
            # JockeyClassPurseRate(),
            #
            # TrainerShowRate(),
            # TrainerTrackPurseRate(),
            #
            # OwnerPercentageBeaten(),
            # TrainerTrackPercentageBeaten(),
            #
            # TrainerTrackShowRate(),
            # TrainerPurseRate(),
            #
            # JockeyTrackShowRate(),
            # BreederShowRate(),
            #
            # HighestOddsWin(),
            #
            # JockeyClassPercentageBeaten(),
            # TrainerSurfacePurseRate(),
            #
            # OwnerPurseRate(),
            # TrainerClassShowRate(),
            #
            # Humidity(),
            #
            # TrainerDistancePercentageBeaten(),
            #
            # JockeyDistancePercentageBeaten(),
            #
            # HorsePercentageBeaten(),
            # AirPressure(),
            #
            # JockeyDistancePurseRate(),
            #
            # AbsoluteTime(),
            #
            # TrainerDistancePurseRate(),
            # HorseBreederPurseRate(),
            #
            # TrainerDistanceShowRate(),
            # Cloudiness(),
            #
            #
            # JockeyDistanceWinRate(),
            #
            # HorseTrainerShowRate(),
            # HorseBreederShowRate(),
            #
            #
            # HorseBreederWinRate(),
            #
            #
            # HasWonAfterLongBreak(),
            # ComingFromLayoff(),
            #
            #
            # HasFewStartsInTwoYears(),
            # HasTongueStrap(),
            #
            #
            #
            # Temperature(),
            # WindSpeed(),
            # WindDirection(),
            # RainVolume(),
            #
            #
            # PreviousFasterThanNumber(),
            #
            # HasFallen(),
            #
            #
            # HorseJockeyWinRate(), HorseTrainerWinRate(),
            #
            # JockeyTrackWinRate(), JockeyClassWinRate(),
            # TrainerDistanceWinRate(), TrainerSurfaceWinRate(), TrainerTrackWinRate(),
            #
            # HorseShowRate(), JockeyShowRate(),
            # DamSireShowRate(),
            #
            # JockeyDistanceShowRate(), JockeySurfaceShowRate(),
            # TrainerSurfaceShowRate(),
            #
            # HorseJockeyPurseRate(), HorseTrainerPurseRate(),
            #
            # JockeySurfacePurseRate(), JockeyTrackPurseRate(),
            # TrainerClassPurseRate(),
            #
            # HorseJockeyPercentageBeaten(), HorseTrainerPercentageBeaten(), HorseBreederPercentageBeaten(),
            #
            # JockeySurfacePercentageBeaten(), JockeyTrackPercentageBeaten(),
            # TrainerSurfacePercentageBeaten(), TrainerClassPercentageBeaten(),
            #
            # MeanSpeedDiff(),
        ]

        return current_race_features + prev_value_features + max_value_features + avg_value_features + time_features + layoff_features

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
