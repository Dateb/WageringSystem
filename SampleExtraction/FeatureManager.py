from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    CurrentRaceClass, CurrentGoing, CurrentRaceTrack, CurrentRaceSurface, CurrentRaceType, CurrentRaceCategory, \
    CurrentRaceTypeDetail, DrawBias, AgeFrom, AgeTo, CurrentHorseCount, WeightAdvantage
from SampleExtraction.Extractors.equipment_based import HasBlinkers, HasVisor, HasHood, HasCheekPieces, HasEyeCovers, \
    HasEyeShield, HasTongueStrap
from SampleExtraction.Extractors.feature_sources import get_feature_sources
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, CurrentRating
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowanceExtractor
from SampleExtraction.Extractors.layoff_based import HasWonAfterLongBreak, ComingFromLayoff, HasOptimalBreak
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestOddsWin, RacebetsWinProbability, \
    BetfairWinMarketWinProbability, BetfairPlaceMarketWinProbability, IsFavorite, IsUnderdog
from SampleExtraction.Extractors.past_performance_based import HasFallen, PulledUpPreviousRace
from SampleExtraction.Extractors.percentage_beaten_based import HorsePercentageBeaten, JockeyPercentageBeaten, \
    TrainerPercentageBeaten, BreederPercentageBeaten, OwnerPercentageBeaten, SirePercentageBeaten, DamPercentageBeaten, \
    DamSirePercentageBeaten, HorseJockeyPercentageBeaten, HorseTrainerPercentageBeaten, HorseBreederPercentageBeaten, \
    JockeyDistancePercentageBeaten, JockeySurfacePercentageBeaten, JockeyTrackPercentageBeaten, \
    JockeyClassPercentageBeaten, TrainerDistancePercentageBeaten, TrainerSurfacePercentageBeaten, \
    TrainerTrackPercentageBeaten, TrainerClassPercentageBeaten
from SampleExtraction.Extractors.potential_based import MaxPastRatingExtractor
from SampleExtraction.Extractors.previous_race_difference_based import RaceClassDifference, \
    HasJockeyChanged, DistanceDifference, HasTrainerChanged, HasTrackChanged, WeightDifference
from SampleExtraction.Extractors.purse_rate_based import HorsePurseRate, JockeyPurseRate, TrainerPurseRate, \
    BreederPurseRate, OwnerPurseRate, SirePurseRate, DamPurseRate, DamSirePurseRate, HorseJockeyPurseRate, \
    HorseTrainerPurseRate, HorseBreederPurseRate, JockeyDistancePurseRate, TrainerDistancePurseRate, \
    JockeySurfacePurseRate, TrainerSurfacePurseRate, JockeyTrackPurseRate, TrainerTrackPurseRate, JockeyClassPurseRate, \
    TrainerClassPurseRate
from SampleExtraction.Extractors.show_rate_based import HorseShowRate, JockeyShowRate, TrainerShowRate, BreederShowRate, \
    OwnerShowRate, DamShowRate, SireShowRate, DamSireShowRate, HorseJockeyShowRate, HorseTrainerShowRate, \
    HorseBreederShowRate, JockeyDistanceShowRate, JockeySurfaceShowRate, JockeyTrackShowRate, JockeyClassShowRate, \
    TrainerDistanceShowRate, TrainerSurfaceShowRate, TrainerTrackShowRate, TrainerClassShowRate
from SampleExtraction.Extractors.speed_based import CurrentSpeedFigure, BestLifeTimeSpeedFigure, MeanSpeedDiff, BaseTime
from SampleExtraction.Extractors.starts_based import LifeTimeStartCount, OneYearStartCount, TwoYearStartCount, \
    HasFewStartsInTwoYears
from SampleExtraction.Extractors.time_based import DayOfYearCos, DayOfYearSin, WeekDayCos, WeekDaySin, MinutesIntoDay, \
    AbsoluteTime
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, SireWinRate, OwnerWinRate, HorseWinRate, \
    JockeyWinRate, HorseJockeyWinRate, HorseBreederWinRate, HorseTrainerWinRate, TrainerWinRate, DamWinRate, \
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
            # RacebetsWinProbability(),
            BetfairWinMarketWinProbability(),
            # BetfairPlaceMarketWinProbability(),
            CurrentSpeedFigure(),
            # BaseTime(),
            MeanSpeedDiff(),

            IsFavorite(), IsUnderdog(),

            DayOfYearCos(), DayOfYearSin(),
            WeekDayCos(), WeekDaySin(),
            MinutesIntoDay(),

            CurrentDistance(), CurrentRaceClass(), CurrentGoing(), CurrentRaceTrack(),
            CurrentRaceSurface(), CurrentRaceType(), CurrentRaceTypeDetail(), CurrentRaceCategory(),

            HasFallen(), HasTrackChanged(), PulledUpPreviousRace(), JockeyWeight(), WeightDifference(),
            DistanceDifference(), WeightAllowanceExtractor(),
            WeightAdvantage(),
        ]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        self.feature_names = [feature.get_name() for feature in self.features]
        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        default_features = [
            Age(), DrawBias(),
            HasTrainerMultipleHorses(),
            AgeFrom(), AgeTo(),
            CurrentRating(),

            HasBlinkers(), HasVisor(), HasHood(), HasCheekPieces(), HasEyeCovers(), HasEyeShield(), HasTongueStrap(),

            AbsoluteTime(),

            BestLifeTimeSpeedFigure(),

            HasOptimalBreak(),
            ComingFromLayoff(),
            HasWonAfterLongBreak(),

            LifeTimeStartCount(),
            OneYearStartCount(),
            TwoYearStartCount(),
            HasFewStartsInTwoYears(),

            HighestOddsWin(),

            Gender(),

            HorseWinRate(), JockeyWinRate(), TrainerWinRate(),
            BreederWinRate(), OwnerWinRate(), SireWinRate(), DamWinRate(), DamSireWinRate(),
            HorseJockeyWinRate(), HorseTrainerWinRate(), HorseBreederWinRate(),

            JockeyDistanceWinRate(), JockeySurfaceWinRate(), JockeyTrackWinRate(), JockeyClassWinRate(),
            TrainerDistanceWinRate(), TrainerSurfaceWinRate(), TrainerTrackWinRate(), TrainerClassWinRate(),

            HorseShowRate(), JockeyShowRate(), TrainerShowRate(),
            BreederShowRate(), OwnerShowRate(), SireShowRate(), DamShowRate(), DamSireShowRate(),
            HorseJockeyShowRate(), HorseTrainerShowRate(), HorseBreederShowRate(),

            JockeyDistanceShowRate(), JockeySurfaceShowRate(), JockeyTrackShowRate(), JockeyClassShowRate(),
            TrainerDistanceShowRate(), TrainerSurfaceShowRate(), TrainerTrackShowRate(), TrainerClassShowRate(),

            HorsePurseRate(), JockeyPurseRate(), TrainerPurseRate(),
            BreederPurseRate(), OwnerPurseRate(), SirePurseRate(), DamPurseRate(), DamSirePurseRate(),
            HorseJockeyPurseRate(), HorseTrainerPurseRate(), HorseBreederPurseRate(),

            JockeyDistancePurseRate(), JockeySurfacePurseRate(), JockeyTrackPurseRate(), JockeyClassPurseRate(),
            TrainerDistancePurseRate(), TrainerSurfacePurseRate(), TrainerTrackPurseRate(), TrainerClassPurseRate(),

            HorsePercentageBeaten(), JockeyPercentageBeaten(), TrainerPercentageBeaten(),
            BreederPercentageBeaten(), OwnerPercentageBeaten(), SirePercentageBeaten(), DamPercentageBeaten(), DamSirePercentageBeaten(),
            HorseJockeyPercentageBeaten(), HorseTrainerPercentageBeaten(), HorseBreederPercentageBeaten(),

            JockeyDistancePercentageBeaten(), JockeySurfacePercentageBeaten(), JockeyTrackPercentageBeaten(), JockeyClassPercentageBeaten(),
            TrainerDistancePercentageBeaten(), TrainerSurfacePercentageBeaten(), TrainerTrackPercentageBeaten(), TrainerClassPercentageBeaten(),

            RaceClassDifference(), HasJockeyChanged(), HasTrainerChanged(),

            MaxPastRatingExtractor(),
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
