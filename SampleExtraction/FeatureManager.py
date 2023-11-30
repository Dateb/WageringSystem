from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    DrawBias, TravelDistance, CurrentRaceTrack, CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceClass, \
    CurrentRaceSurface, CurrentGoing, CurrentRaceCategory, AgeFrom, AgeTo, CurrentPurse
from SampleExtraction.Extractors.equipment_based import HasFirstTimeBlinkers, HasFirstTimeVisor, HasFirstTimeHood, \
    HasFirstTimeCheekPieces, HasBlinkers, HasHood, HasCheekPieces, HasVisor, HasEyeCovers, HasEyeShield
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, CurrentRating, PostPosition
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowance, JockeyPlacePercentile
from SampleExtraction.Extractors.layoff_based import PreviousRaceLayoff, SameTrackLayoff, SameClassLayoff, SameSurfaceLayoff
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.pedigree_based import DamPlacePercentile, DamRelativeDistanceBehind, \
    SireRelativeDistanceBehind, SirePlacePercentile, SireSiblingsMomentum, DamSiblingsMomentum, \
    SireAndDamSiblingsMomentum, DamSireSiblingsMomentum
from SampleExtraction.Extractors.potential_based import BestClassPlace
from SampleExtraction.Extractors.previous_race_based import PreviousRelativeDistanceBehind, PreviousWinProbability, \
    PreviousPlacePercentile, \
    PreviousSameSurfaceWinProbability, PreviousSameTrackWinProbability, PreviousSameRaceClassWinProbability, \
    PreviousSameSurfacePlacePercentile, PreviousSameTrackPlacePercentile, PreviousSameRaceClassPlacePercentile, \
    PreviousSameSurfaceRelativeDistanceBehind, \
    PreviousSameTrackRelativeDistanceBehind, PreviousSameRaceClassRelativeDistanceBehind, PulledUpPreviousRace, \
    PreviousSameSurfaceVelocity, PreviousSameTrackVelocity, PreviousSameRaceClassVelocity, HasPreviousRaces
from SampleExtraction.Extractors.previous_race_difference_based import RaceClassDifference, \
    DistanceDifference, WeightDifference, RaceGoingDifference, AllowanceDifference, OwnerWinRateDifference
from SampleExtraction.Extractors.purse_based import HorsePurseRate, DamPurseRate
from SampleExtraction.Extractors.scratched_based import HorseScratchedRate, JockeyScratchedRate, TrainerScratchedRate, \
    HorsePulledUpRate
from SampleExtraction.Extractors.show_rate_based import HorseShowRate
from SampleExtraction.Extractors.starts_based import LifeTimeStartCount
from SampleExtraction.Extractors.time_based import WeekDayCos, WeekDaySin, MinutesIntoDay, MonthCos, MonthSin, \
    DayOfMonthCos, DayOfMonthSin
from SampleExtraction.Extractors.trainer_based import TrainerPlacePercentile
from SampleExtraction.Extractors.velocity_based import PreviousVelocity, DamVelocity, SireVelocity
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, OwnerWinRate, HorseWinRate, \
    HorsePlacePercentile, \
    HorseMomentum, HorseWinProbability, WindowTimeLength
from SampleExtraction.feature_sources.init import FEATURE_SOURCES


class FeatureManager:

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features

        self.base_features = [
            # HasWon(),
            # BetfairWinMarketWinProbability(),

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
        window_sizes = [3, 5, 7]
        win_prob_features = [HorseWinProbability(window_size=i) for i in window_sizes]
        win_rate_features = [HorseWinRate(window_size=i) for i in window_sizes]
        show_rate_features = [HorseShowRate(window_size=i) for i in window_sizes]
        place_percentile_features = [HorsePlacePercentile(window_size=i) for i in window_sizes]
        momentum_features = [HorseMomentum(window_size=i) for i in window_sizes]
        window_time_length_features = [WindowTimeLength(window_size=i) for i in window_sizes]

        default_features = [
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
            # PostPosition(),

            HorsePulledUpRate(),
            PulledUpPreviousRace(),

            HorsePurseRate(),

            MinutesIntoDay(),

            MonthCos(),
            MonthSin(),

            DayOfMonthCos(),
            DayOfMonthSin(),

            WeekDaySin(),
            WeekDayCos(),

            HasPreviousRaces(),

            PreviousWinProbability(),

            PreviousSameSurfaceWinProbability(),
            PreviousSameTrackWinProbability(),
            PreviousSameRaceClassWinProbability(),

            PreviousVelocity(),

            PreviousPlacePercentile(),

            PreviousSameSurfacePlacePercentile(),
            PreviousSameTrackPlacePercentile(),
            PreviousSameRaceClassPlacePercentile(),

            PreviousRelativeDistanceBehind(),

            PreviousSameSurfaceRelativeDistanceBehind(),
            PreviousSameTrackRelativeDistanceBehind(),
            PreviousSameRaceClassRelativeDistanceBehind(),

            PreviousRaceLayoff(),

            SameTrackLayoff(),
            SameClassLayoff(),
            SameSurfaceLayoff(),

            JockeyPlacePercentile(),
            TrainerPlacePercentile(),

            JockeyWeight(),
            WeightAllowance(),

            DistanceDifference(),
            RaceGoingDifference(),
            RaceClassDifference(),

            WeightDifference(),
            AllowanceDifference(),

            OwnerWinRateDifference(),

            #TODO: Use momentum for draw bias
            DrawBias(),

            TravelDistance(),

            HorseScratchedRate(),
            JockeyScratchedRate(),
            TrainerScratchedRate(),

            HasTrainerMultipleHorses(),

            BreederWinRate(), OwnerWinRate(),

            DamPlacePercentile(), DamRelativeDistanceBehind(),
            SirePlacePercentile(), SireRelativeDistanceBehind(),

            SireSiblingsMomentum(),
            DamSiblingsMomentum(),
            SireAndDamSiblingsMomentum(),
            DamSireSiblingsMomentum(),

            # HasBlinkers(), HasHood(), HasCheekPieces(),
            # HasVisor(), HasEyeCovers(), HasEyeShield(),

            BestClassPlace(),
            LifeTimeStartCount(),

            DamVelocity(), SireVelocity(),

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
            # HorseJockeyShowRate(),
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
        ] + win_prob_features + win_rate_features + show_rate_features + place_percentile_features + momentum_features + window_time_length_features

        return default_features

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
