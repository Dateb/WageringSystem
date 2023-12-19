from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor, FeatureSourceExtractor
from SampleExtraction.Extractors.current_race_based import CurrentRaceTrack, CurrentRaceClass, CurrentRaceSurface, \
    CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceCategory, CurrentGoing, CurrentDistance, CurrentPurse, AgeFrom, \
    AgeTo
from SampleExtraction.Extractors.horse_attributes_based import CurrentRating, Age, Gender
from SampleExtraction.Extractors.jockey_based import CurrentJockeyWeight, WeightAllowance
from SampleExtraction.Extractors.time_based import MinutesIntoDay, MonthCos, MonthSin, DayOfMonthCos, DayOfMonthSin, \
    WeekDaySin, WeekDayCos
from SampleExtraction.feature_sources.feature_sources import FeatureValueGroup
from SampleExtraction.feature_sources.init import FEATURE_SOURCES, previous_value_source, avg_window_3_min_obs_3_source, \
    avg_window_5_min_obs_3_source, avg_window_7_min_obs_3_source
from SampleExtraction.feature_sources.value_calculators import win_probability, momentum


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
        horse_momentum = FeatureValueGroup(["subject_id"], momentum)

        horse_surface_win_prob = FeatureValueGroup(["subject_id", "surface"], win_probability)
        horse_track_win_prob = FeatureValueGroup(["subject_id", "track_name"], win_probability)
        horse_class_win_prob = FeatureValueGroup(["subject_id", "race_class"], win_probability)

        jockey_win_prob = FeatureValueGroup(["jockey_name"], win_probability)
        jockey_momentum = FeatureValueGroup(["jockey_name"], momentum)

        trainer_win_prob = FeatureValueGroup(["trainer_name"], win_probability)
        trainer_momentum = FeatureValueGroup(["trainer_name"], momentum)

        prev_value_features = [
            FeatureSourceExtractor(previous_value_source, horse_win_prob),
            FeatureSourceExtractor(previous_value_source, horse_momentum),

            FeatureSourceExtractor(previous_value_source, horse_surface_win_prob),
            FeatureSourceExtractor(previous_value_source, horse_track_win_prob),
            FeatureSourceExtractor(previous_value_source, horse_class_win_prob),

            FeatureSourceExtractor(previous_value_source, jockey_win_prob),
            FeatureSourceExtractor(previous_value_source, jockey_momentum),

            FeatureSourceExtractor(previous_value_source, trainer_win_prob),
            FeatureSourceExtractor(previous_value_source, trainer_momentum),
        ]

        avg_value_features = [
            FeatureSourceExtractor(avg_window_3_min_obs_3_source, horse_win_prob),
            FeatureSourceExtractor(avg_window_5_min_obs_3_source, horse_win_prob),
            FeatureSourceExtractor(avg_window_7_min_obs_3_source, horse_win_prob),

            FeatureSourceExtractor(avg_window_3_min_obs_3_source, horse_momentum),
            FeatureSourceExtractor(avg_window_5_min_obs_3_source, horse_momentum),
            FeatureSourceExtractor(avg_window_7_min_obs_3_source, horse_momentum)
        ]

        current_race_features = [
            CurrentRaceTrack(),
            CurrentRaceClass(),
            CurrentRaceSurface(),

            CurrentRaceType(),
            CurrentRaceTypeDetail(),
            CurrentRaceCategory(),

            CurrentGoing(),
            CurrentDistance(),
            CurrentPurse(),

            CurrentRating(),

            Age(),
            Gender(),

            AgeFrom(), AgeTo(),
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

        default_features = [
            # CurrentJockeyWeight(),
            # WeightAllowance(),

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
            #
            # PreviousMomentum(),
            #
            # PreviousSameSurfaceMomentum(),
            # PreviousSameTrackMomentum(),
            # PreviousSameRaceClassMomentum(),
            #
            # PreviousPlacePercentile(),
            #
            # PreviousSameSurfacePlacePercentile(),
            # PreviousSameTrackPlacePercentile(),
            # PreviousSameRaceClassPlacePercentile(),
            #
            # PreviousRaceLayoff(),
            #
            # SameTrackLayoff(),
            # SameClassLayoff(),
            # SameSurfaceLayoff(),
            #
            # JockeyMomentum(),
            # TrainerMomentum(),
            #
            #
            # DistanceDifference(),
            # RaceGoingDifference(),
            # RaceClassDifference(),
            #
            # WeightDifference(),
            # AllowanceDifference(),
            #
            # OwnerWinRateDifference(),
            #
            # DrawBias(),
            #
            # TravelDistance(),
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
            # HasBlinkers(), HasHood(), HasCheekPieces(),
            # HasVisor(), HasEyeCovers(), HasEyeShield(),
            #
            # BestClassPlace(),
            # LifeTimeStartCount(),
            #
            # DamMomentum(), SireMomentum(),
            #
            # BreederMomentum(), OwnerMomentum(),
            #
            # HorseJockeyWinProbability(),
            # HorseJockeyPlacePercentile(),
            # HorseJockeyMomentum(),
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

        return current_race_features + prev_value_features + avg_value_features + time_features

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
        feature_sources = FEATURE_SOURCES

        if race_card.has_results:
            for feature_source in feature_sources:
                feature_source.pre_update(race_card)

    def post_update_feature_sources(self, race_cards: List[RaceCard]) -> None:
        feature_sources = FEATURE_SOURCES

        for race_card in race_cards:
            if race_card.has_results and race_card.feature_source_validity:
                for feature_source in feature_sources:
                    feature_source.post_update(race_card)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
