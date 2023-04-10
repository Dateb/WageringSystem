from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.current_race_based import CurrentDistance, \
    CurrentRaceClass, CurrentRaceTrack, \
    DrawBias, CurrentOpponentCount, WeightAdvantage, TravelDistance, Temperature, \
    AirPressure, Humidity, WindSpeed, WindDirection, Cloudiness, RainVolume
from SampleExtraction.Extractors.feature_sources import get_feature_sources
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, CurrentRating, ShiftedOdds
from SampleExtraction.Extractors.jockey_based import JockeyWeight, WeightAllowanceExtractor
from SampleExtraction.Extractors.layoff_based import HasWonAfterLongBreak, ComingFromLayoff, HasOptimalBreak
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestOddsWin, \
    BetfairWinMarketWinProbability, IsFavorite, IsUnderdog, \
    IndustryMarketWinProbabilityDiff
from SampleExtraction.Extractors.percentage_beaten_based import HorsePercentageBeaten, JockeyPercentageBeaten, \
    TrainerPercentageBeaten, BreederPercentageBeaten, OwnerPercentageBeaten, SirePercentageBeaten, DamPercentageBeaten, \
    DamSirePercentageBeaten, HorseJockeyPercentageBeaten, HorseTrainerPercentageBeaten, HorseBreederPercentageBeaten, \
    JockeyDistancePercentageBeaten, JockeySurfacePercentageBeaten, JockeyTrackPercentageBeaten, \
    JockeyClassPercentageBeaten, TrainerDistancePercentageBeaten, TrainerSurfacePercentageBeaten, \
    TrainerTrackPercentageBeaten, TrainerClassPercentageBeaten
from SampleExtraction.Extractors.potential_based import MaxPastRatingExtractor
from SampleExtraction.Extractors.previous_race_based import PreviousFasterThanNumber, \
    PreviousSlowerThanNumber, PreviousRelativeDistanceBehind
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

    HORSE_PADDING_SIZE = 30

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features

        self.base_features: List[FeatureExtractor] = [
            ShiftedOdds(),
            CurrentRaceTrack(),
            PreviousSlowerThanNumber(),
            PreviousRelativeDistanceBehind(),
        ]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        self.feature_names = []
        for i in range(0, self.HORSE_PADDING_SIZE):
            self.feature_names += [f"{feature.get_name()}_{i + 1}" for feature in self.features]
        self.n_features = len(self.features)

        self.columns = RaceCard.BASE_ATTRIBUTE_NAMES + Horse.BASE_ATTRIBUTE_NAMES + self.feature_names

    def get_search_features(self) -> List[FeatureExtractor]:
        default_features = [
            CurrentOpponentCount(),

            PreviousFasterThanNumber(),

            CurrentSpeedFigure(),
            DistanceDifference(),

            TravelDistance(),
            Gender(),
            MinutesIntoDay(),
            Age(),
            CurrentDistance(),
            JockeyWeight(),
            WeekDayCos(), WeekDaySin(),

            CurrentRaceClass(),

            WeightDifference(),
            WeightAllowanceExtractor(),
            HighestOddsWin(),

            DrawBias(),
            CurrentRating(),

            AbsoluteTime(),

            BestLifeTimeSpeedFigure(),

            ComingFromLayoff(),

            LifeTimeStartCount(),
            OneYearStartCount(),
            TwoYearStartCount(),

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
            BreederPercentageBeaten(), OwnerPercentageBeaten(), SirePercentageBeaten(), DamPercentageBeaten(),
            DamSirePercentageBeaten(),
            HorseJockeyPercentageBeaten(), HorseTrainerPercentageBeaten(), HorseBreederPercentageBeaten(),

            JockeyDistancePercentageBeaten(), JockeySurfacePercentageBeaten(), JockeyTrackPercentageBeaten(),
            JockeyClassPercentageBeaten(),
            TrainerDistancePercentageBeaten(), TrainerSurfacePercentageBeaten(), TrainerTrackPercentageBeaten(),
            TrainerClassPercentageBeaten(),

            RaceClassDifference(),

            MaxPastRatingExtractor(),

            DayOfYearSin(),
            DayOfYearCos(),
            WeightAdvantage(),

            # Temperature(),
            # AirPressure(),
            # Humidity(),
            # WindSpeed(),
            # WindDirection(),
            # Cloudiness(),
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

    @staticmethod
    def get_feature_names(feature_subset: List[FeatureExtractor]) -> List[str]:
        feature_names = []
        #TODO: Use variable for padding size
        for i in range(0, 30):
            feature_names += [f"{feature.get_name()}_{i + 1}" for feature in feature_subset]

        return feature_names

