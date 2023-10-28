from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    CurrentRaceClass, CurrentGoing, CurrentRaceTrack, CurrentRaceSurface, CurrentRaceType, CurrentRaceCategory, \
    CurrentRaceTypeDetail, DrawBias, AgeFrom, AgeTo, CurrentHorseCount, WeightAdvantage, TravelDistance, Temperature, \
    AirPressure, Humidity, WindSpeed, WindDirection, Cloudiness, RainVolume, WeatherType
from SampleExtraction.Extractors.equipment_based import HasBlinkers, HasVisor, HasHood, HasCheekPieces, HasEyeCovers, \
    HasEyeShield, HasTongueStrap, HasFirstTimeBlinkers, HasFirstTimeVisor, HasFirstTimeHood, HasFirstTimeCheekPieces
from SampleExtraction.Extractors.feature_sources import get_feature_sources
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, CurrentRating, HasWon
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowance, JockeyWinRate, JockeyPlaceRate, \
    JockeyEarningsRate
from SampleExtraction.Extractors.layoff_based import HasWonAfterLongBreak, ComingFromLayoff, HasOptimalBreak, \
    PreviousRaceLayoff, SameTrackLayoff, SameClassLayoff, SameSurfaceLayoff
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestLifetimeWinProbability, RacebetsWinProbability, \
    BetfairWinMarketWinProbability, BetfairPlaceMarketWinProbability, IsFavorite, IsUnderdog, \
    IndustryMarketWinProbabilityDiff, BetfairOverround
from SampleExtraction.Extractors.past_performance_based import HasFallen, HasPastPerformance
from SampleExtraction.Extractors.pedigree_based import DamPlacePercentile, DamRelativeDistanceBehind, \
    SireRelativeDistanceBehind, SirePlacePercentile, SireSiblingsPlacePercentile, DamSiblingsPlacePercentile, \
    SireAndDamSiblingsPlacePercentile, DamSireSiblingsPlacePercentile
from SampleExtraction.Extractors.percentage_beaten_based import HorsePercentageBeaten, JockeyPercentageBeaten, \
    TrainerPercentageBeaten, BreederPercentageBeaten, OwnerPercentageBeaten, SirePercentageBeaten, DamPercentageBeaten, \
    DamSirePercentageBeaten, HorseJockeyPercentageBeaten, HorseTrainerPercentageBeaten, HorseBreederPercentageBeaten, \
    JockeyDistancePercentageBeaten, JockeySurfacePercentageBeaten, JockeyTrackPercentageBeaten, \
    JockeyClassPercentageBeaten, TrainerDistancePercentageBeaten, TrainerSurfacePercentageBeaten, \
    TrainerTrackPercentageBeaten, TrainerClassPercentageBeaten
from SampleExtraction.Extractors.potential_based import MaxPastRatingExtractor, HorseTopFinish
from SampleExtraction.Extractors.previous_race_based import PreviousFasterThanFraction, PulledUpPreviousRace, \
    PreviousSlowerThanFraction, PreviousRelativeDistanceBehind, PreviousWinProbability, PreviousPlacePercentile, \
    PreviousSameSurfaceWinProbability, PreviousSameTrackWinProbability, PreviousSameRaceClassWinProbability, \
    PreviousSameSurfacePlacePercentile, PreviousSameTrackPlacePercentile, PreviousSameRaceClassPlacePercentile, \
    PreviousSameGoingWinProbability, PreviousSameGoingPlacePercentile, PreviousSameSurfaceRelativeDistanceBehind, \
    PreviousSameTrackRelativeDistanceBehind, PreviousSameRaceClassRelativeDistanceBehind
from SampleExtraction.Extractors.previous_race_difference_based import RaceClassDifference, \
    HasJockeyChanged, DistanceDifference, HasTrainerChanged, HasTrackChanged, WeightDifference, IsSecondRaceForJockey, \
    RaceGoingDifference
from SampleExtraction.Extractors.purse_based import HorsePurseRate, JockeyPurseRate, TrainerPurseRate, \
    BreederPurseRate, OwnerPurseRate, SirePurseRate, DamPurseRate, DamSirePurseRate, HorseJockeyPurseRate, \
    HorseTrainerPurseRate, HorseBreederPurseRate, JockeyDistancePurseRate, TrainerDistancePurseRate, \
    JockeySurfacePurseRate, TrainerSurfacePurseRate, JockeyTrackPurseRate, TrainerTrackPurseRate, JockeyClassPurseRate, \
    TrainerClassPurseRate
from SampleExtraction.Extractors.scratched_based import HorseScratchedRate, JockeyScratchedRate, TrainerScratchedRate
from SampleExtraction.Extractors.show_rate_based import HorseShowRate, JockeyShowRate, TrainerShowRate, BreederShowRate, \
    OwnerShowRate, DamShowRate, SireShowRate, DamSireShowRate, HorseJockeyShowRate, HorseTrainerShowRate, \
    HorseBreederShowRate, JockeyDistanceShowRate, JockeySurfaceShowRate, JockeyTrackShowRate, JockeyClassShowRate, \
    TrainerDistanceShowRate, TrainerSurfaceShowRate, TrainerTrackShowRate, TrainerClassShowRate
from SampleExtraction.Extractors.speed_based import CurrentSpeedFigure, BestLifeTimeSpeedFigure, MeanSpeedDiff
from SampleExtraction.Extractors.starts_based import LifeTimeStartCount, OneYearStartCount, TwoYearStartCount, \
    HasFewStartsInTwoYears, LifeTimePlaceCount, LifeTimeWinCount
from SampleExtraction.Extractors.time_based import DayOfYearCos, DayOfYearSin, WeekDayCos, WeekDaySin, MinutesIntoDay, \
    AbsoluteTime
from SampleExtraction.Extractors.trainer_based import TrainerWinRate, TrainerPlaceRate, TrainerEarningsRate
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, OwnerWinRate, HorseWinRate, \
    HorseJockeyWinRate, HorseBreederWinRate, HorseTrainerWinRate, \
    DamSireWinRate, JockeyDistanceWinRate, JockeySurfaceWinRate, TrainerDistanceWinRate, TrainerSurfaceWinRate, \
    JockeyTrackWinRate, TrainerTrackWinRate, JockeyClassWinRate, TrainerClassWinRate, HorsePlacePercentile, \
    HorseRelativeDistanceBehind


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
        self.numerical_feature_names = [feature.get_name() for feature in self.features if not feature.is_categorical]
        self.categorical_feature_names = [feature.get_name() for feature in self.features if feature.is_categorical]
        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        default_features = [
            # CurrentRaceTrack(),
            # CurrentRaceType(),
            # CurrentRaceTypeDetail(),

            # Does not work cause of new categories:
            # CurrentRaceCategory(),

            # Does not work because of error: ValueError: invalid literal for int() with base 10: 'B'
            CurrentRaceClass(),

            # HasBlinkers(), HasHood(), HasCheekPieces(),
            # HasVisor(), HasEyeCovers(), HasEyeShield(),

            # HasFirstTimeBlinkers(), HasFirstTimeVisor(), HasFirstTimeHood(), HasFirstTimeCheekPieces(),

            PreviousWinProbability(),

            CurrentRaceSurface(),
            Gender(),

            HorseWinRate(),
            HorseShowRate(),
            HorsePlacePercentile(),
            HorseRelativeDistanceBehind(),
            HorsePurseRate(),

            CurrentDistance(),

            MinutesIntoDay(),

            DayOfYearSin(),
            DayOfYearCos(),

            WeekDaySin(),
            WeekDayCos(),

            PreviousSameSurfaceWinProbability(),
            PreviousSameTrackWinProbability(),
            PreviousSameRaceClassWinProbability(),

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

            JockeyWinRate(),
            JockeyPlaceRate(),
            JockeyEarningsRate(),

            TrainerWinRate(),
            TrainerPlaceRate(),
            TrainerEarningsRate(),

            JockeyWeight(),
            WeightAllowance(),
            Age(),

            DistanceDifference(),
            RaceGoingDifference(),
            RaceClassDifference(),

            WeightDifference(),

            DrawBias(),
            TravelDistance(),

            HorseScratchedRate(),

            HasTrainerMultipleHorses(),

            BreederWinRate(), OwnerWinRate(),

            DamPlacePercentile(), DamRelativeDistanceBehind(),
            SirePlacePercentile(), SireRelativeDistanceBehind(),

            SireSiblingsPlacePercentile(),
            DamSiblingsPlacePercentile(),
            SireAndDamSiblingsPlacePercentile(),
            DamSireSiblingsPlacePercentile(),

            # JockeyScratchedRate(),
            # TrainerScratchedRate(),

            # DamPercentageBeaten(), SirePercentageBeaten(),
            # DamPurseRate(), SirePurseRate(),

            # HighestLifetimeWinProbability(),

            # Needs improvement in regards with different start counts

            # CurrentSpeedFigure(),

            # CurrentRating(),
            #
            # LifeTimeStartCount(),
            # LifeTimeWinCount(),
            # LifeTimePlaceCount(),
            #
            # #
            # #
            #
            # HasJockeyChanged(),
            # HasTrainerChanged(),

            # CurrentGoing(),

            ## Uses form table:

            # HasPastPerformance(),
            # HasTrackChanged(),

            # OneYearStartCount(),
            # TwoYearStartCount(),

            # Not using form table:
            #
            #
            # DamSireWinRate(),

            #-----------------------------------------------------------------
            #Needs improvement:


            # HorseTopFinish()
            # MaxPastRatingExtractor(),

            # BestLifeTimeSpeedFigure(),

            # Not helping but not hurting:

            # Increasing loss when included:

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
            # SireShowRate(),
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
            # DamShowRate(),
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
            # CurrentRaceType(),
            #
            # HasFewStartsInTwoYears(),
            # HasTongueStrap(),
            #
            #
            # PulledUpPreviousRace(),
            #
            # Temperature(),
            # WindSpeed(),
            # WindDirection(),
            # RainVolume(),
            #
            #
            # PreviousFasterThanNumber(),
            #
            # CurrentRaceSurface(),
            # HasFallen(),
            # IsUnderdog(),
            #
            #
            # AgeFrom(), AgeTo(),
            #
            #
            #
            # HasOptimalBreak(),
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
            # CurrentRaceTypeDetail(),
        ]

        return default_features

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
        feature_sources = get_feature_sources()

        if race_card.has_results:
            for feature_source in feature_sources:
                feature_source.pre_update(race_card)

    def post_update_feature_sources(self, race_cards: List[RaceCard]) -> None:
        feature_sources = get_feature_sources()

        for race_card in race_cards:
            if race_card.has_results and race_card.feature_source_validity:
                for feature_source in feature_sources:
                    feature_source.post_update(race_card)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
