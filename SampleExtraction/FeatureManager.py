from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    DrawBias, TravelDistance, CurrentRaceTrack, CurrentRaceType, CurrentRaceTypeDetail, CurrentRaceClass, \
    CurrentRaceSurface, CurrentGoing, CurrentRaceCategory
from SampleExtraction.Extractors.equipment_based import HasFirstTimeBlinkers, HasFirstTimeVisor, HasFirstTimeHood, \
    HasFirstTimeCheekPieces
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowance, JockeyWinRate, JockeyPlaceRate, \
    JockeyEarningsRate
from SampleExtraction.Extractors.layoff_based import PreviousRaceLayoff, SameTrackLayoff, SameClassLayoff, SameSurfaceLayoff
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.pedigree_based import DamPlacePercentile, DamRelativeDistanceBehind, \
    SireRelativeDistanceBehind, SirePlacePercentile, SireSiblingsPlacePercentile, DamSiblingsPlacePercentile, \
    SireAndDamSiblingsPlacePercentile, DamSireSiblingsPlacePercentile
from SampleExtraction.Extractors.previous_race_based import PreviousRelativeDistanceBehind, PreviousWinProbability, PreviousPlacePercentile, \
    PreviousSameSurfaceWinProbability, PreviousSameTrackWinProbability, PreviousSameRaceClassWinProbability, \
    PreviousSameSurfacePlacePercentile, PreviousSameTrackPlacePercentile, PreviousSameRaceClassPlacePercentile, \
    PreviousSameSurfaceRelativeDistanceBehind, \
    PreviousSameTrackRelativeDistanceBehind, PreviousSameRaceClassRelativeDistanceBehind
from SampleExtraction.Extractors.previous_race_difference_based import RaceClassDifference, \
    DistanceDifference, WeightDifference, RaceGoingDifference, AllowanceDifference, JockeyPlaceRateDifference
from SampleExtraction.Extractors.purse_based import HorsePurseRate
from SampleExtraction.Extractors.scratched_based import HorseScratchedRate
from SampleExtraction.Extractors.show_rate_based import HorseShowRate
from SampleExtraction.Extractors.speed_based import CurrentSpeedFigure
from SampleExtraction.Extractors.time_based import WeekDayCos, WeekDaySin, MinutesIntoDay, MonthCos, MonthSin, \
    DayOfMonthCos, DayOfMonthSin
from SampleExtraction.Extractors.trainer_based import TrainerWinRate, TrainerPlaceRate, TrainerEarningsRate
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, OwnerWinRate, HorseWinRate, \
    HorsePlacePercentile, \
    HorseRelativeDistanceBehind, HorseWinProbability
from SampleExtraction.feature_sources.init import get_feature_sources


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
        default_features = [
            # CurrentSpeedFigure(),

            CurrentRaceTrack(),
            CurrentRaceClass(),
            CurrentRaceSurface(),
            CurrentRaceType(),
            CurrentRaceTypeDetail(),
            CurrentRaceCategory(),

            # HasBlinkers(), HasHood(), HasCheekPieces(),
            # HasVisor(), HasEyeCovers(), HasEyeShield(),

            # HasFirstTimeBlinkers(), HasFirstTimeVisor(), HasFirstTimeHood(), HasFirstTimeCheekPieces(),

            Gender(),
            CurrentGoing(),

            PreviousWinProbability(),

            HorseWinProbability(),
            HorseWinRate(),
            HorseShowRate(),
            HorsePlacePercentile(),
            HorseRelativeDistanceBehind(),
            HorsePurseRate(),

            CurrentDistance(),

            MinutesIntoDay(),

            MonthCos(),
            MonthSin(),

            DayOfMonthCos(),
            DayOfMonthSin(),

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
            AllowanceDifference(),
            JockeyPlaceRateDifference(),

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

            # CurrentRating(),
            #
            # LifeTimeStartCount(),
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
        ]

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
