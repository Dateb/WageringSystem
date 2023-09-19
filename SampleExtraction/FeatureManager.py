from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    CurrentRaceClass, CurrentGoing, CurrentRaceTrack, CurrentRaceSurface, CurrentRaceType, CurrentRaceCategory, \
    CurrentRaceTypeDetail, DrawBias, AgeFrom, AgeTo, CurrentHorseCount, WeightAdvantage, TravelDistance, Temperature, \
    AirPressure, Humidity, WindSpeed, WindDirection, Cloudiness, RainVolume, WeatherType
from SampleExtraction.Extractors.equipment_based import HasBlinkers, HasVisor, HasHood, HasCheekPieces, HasEyeCovers, \
    HasEyeShield, HasTongueStrap
from SampleExtraction.Extractors.feature_sources import get_feature_sources
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, CurrentRating, HasWon
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowance, JockeyWinRate, JockeyPlaceRate, \
    JockeyEarningsRate
from SampleExtraction.Extractors.layoff_based import HasWonAfterLongBreak, ComingFromLayoff, HasOptimalBreak, Layoff
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestOddsWin, RacebetsWinProbability, \
    BetfairWinMarketWinProbability, BetfairPlaceMarketWinProbability, IsFavorite, IsUnderdog, \
    IndustryMarketWinProbabilityDiff, BetfairOverround
from SampleExtraction.Extractors.past_performance_based import HasFallen, HasPastPerformance
from SampleExtraction.Extractors.percentage_beaten_based import HorsePercentageBeaten, JockeyPercentageBeaten, \
    TrainerPercentageBeaten, BreederPercentageBeaten, OwnerPercentageBeaten, SirePercentageBeaten, DamPercentageBeaten, \
    DamSirePercentageBeaten, HorseJockeyPercentageBeaten, HorseTrainerPercentageBeaten, HorseBreederPercentageBeaten, \
    JockeyDistancePercentageBeaten, JockeySurfacePercentageBeaten, JockeyTrackPercentageBeaten, \
    JockeyClassPercentageBeaten, TrainerDistancePercentageBeaten, TrainerSurfacePercentageBeaten, \
    TrainerTrackPercentageBeaten, TrainerClassPercentageBeaten
from SampleExtraction.Extractors.potential_based import MaxPastRatingExtractor, HorseTopFinish
from SampleExtraction.Extractors.previous_race_based import PreviousFasterThanFraction, PulledUpPreviousRace, \
    PreviousSlowerThanFraction, PreviousRelativeDistanceBehind, PreviousWinProbability, PreviousPlacePercentile
from SampleExtraction.Extractors.previous_race_difference_based import RaceClassDifference, \
    HasJockeyChanged, DistanceDifference, HasTrainerChanged, HasTrackChanged, WeightDifference, IsSecondRaceForJockey
from SampleExtraction.Extractors.purse_based import HorsePurseRate, JockeyPurseRate, TrainerPurseRate, \
    BreederPurseRate, OwnerPurseRate, SirePurseRate, DamPurseRate, DamSirePurseRate, HorseJockeyPurseRate, \
    HorseTrainerPurseRate, HorseBreederPurseRate, JockeyDistancePurseRate, TrainerDistancePurseRate, \
    JockeySurfacePurseRate, TrainerSurfacePurseRate, JockeyTrackPurseRate, TrainerTrackPurseRate, JockeyClassPurseRate, \
    TrainerClassPurseRate, AveragePurse
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
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, SireWinRate, OwnerWinRate, HorseWinRate, \
    HorseJockeyWinRate, HorseBreederWinRate, HorseTrainerWinRate, DamWinRate, \
    DamSireWinRate, JockeyDistanceWinRate, JockeySurfaceWinRate, TrainerDistanceWinRate, TrainerSurfaceWinRate, \
    JockeyTrackWinRate, TrainerTrackWinRate, JockeyClassWinRate, TrainerClassWinRate


class FeatureManager:

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features

        self.base_features = [
            # HasWon(),
            # CurrentRaceTrack(),
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
            PreviousWinProbability(),
            RaceClassDifference(),

            PreviousPlacePercentile(),
            PreviousRelativeDistanceBehind(),
            DistanceDifference(),

            ## Uses form table:

            # HasPastPerformance(),
            # WeightDifference(),
            # HasTrackChanged(),
            # Layoff(),

            # OneYearStartCount(),
            # TwoYearStartCount(),

            # Not using form table:
            #
            # LifeTimeStartCount(),
            # LifeTimeWinCount(),
            # LifeTimePlaceCount(),
            #
            #
            # Age(),
            # CurrentSpeedFigure(),
            #
            # JockeyWinRate(),
            # JockeyPlaceRate(),
            # JockeyEarningsRate(),
            #
            # WeightAllowance(),
            #
            # TrainerWinRate(),
            # TrainerPlaceRate(),
            # TrainerEarningsRate(),
            #
            # Gender(),
            # JockeyWeight(),
            #
            # BreederWinRate(), OwnerWinRate(),
            # DamWinRate(), SireWinRate(),
            # CurrentRating(),
            #
            # HasBlinkers(), HasHood(), HasCheekPieces(),
            # HasTrainerMultipleHorses(),

            # DayOfYearSin(),
            # DayOfYearCos(),
            #
            # WeekDaySin(),
            # WeekDayCos(),
            #
            # MinutesIntoDay(),

            # HorseWinRate(),
            # DamSireWinRate(),

            #-----------------------------------------------------------------
            #Needs improvement:

            # HorsePurseRate(),

            # HorseTopFinish()
            # MaxPastRatingExtractor(),

            # TravelDistance(),

            # BestLifeTimeSpeedFigure(),

            # Not helping but not hurting:
            # HasJockeyChanged(),
            # HasTrainerChanged(),

            # Increasing loss when included:

            # PreviousFasterThanFraction(),
            # PreviousSlowerThanFraction(),
            # JockeySurfaceWinRate(),
            # AveragePurse(),

            # Not tested:

            # CurrentRaceClass(),
            # WeightAdvantage(),
            # CurrentRaceCategory(),
            #
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
            # SirePurseRate(),
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
            # DamPurseRate(),
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
            # HasVisor(),
            # CurrentRaceType(),
            #
            # HasFewStartsInTwoYears(),
            # HasTongueStrap(),
            #
            # HasEyeCovers(),
            # HasEyeShield(),
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
            # WeekDayCos(),
            #
            # CurrentGoing(),
            #
            # DrawBias(),
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
            # SirePercentageBeaten(), DamPercentageBeaten(),
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
