from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.AveragePlaceLifetime import AveragePlaceLifetimeExtractor
from SampleExtraction.Extractors.AveragePlaceSurfaceExtractor import AveragePlaceSurfaceExtractor
from SampleExtraction.Extractors.AveragePlaceTrackExtractor import AveragePlaceTrackExtractor
from SampleExtraction.Extractors.current_race_based import HasTrainerMultipleHorses, CurrentDistance, \
    CurrentRaceClass, CurrentGoing, CurrentRaceTrack, CurrentRaceSurface, CurrentRaceType, CurrentRaceCategory, \
    CurrentRaceTypeDetail, DrawBias
from SampleExtraction.Extractors.feature_sources import get_feature_sources
from SampleExtraction.Extractors.horse_attributes_based import CurrentOdds, Age, Gender, CurrentRating, HasBlinker
from SampleExtraction.Extractors.jockey_based import JockeyWeight
from SampleExtraction.Extractors.layoff_based import HasOptimalBreak, HasLongBreak, \
    HasVeryLongBreak, HasWonAfterLongBreak
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestOddsWin
from SampleExtraction.Extractors.previous_race_difference_based import DistanceDifference, RaceClassDifference, \
    HasJockeyChanged
from SampleExtraction.Extractors.speed_based import CurrentSpeedFigure
from SampleExtraction.Extractors.starts_based import LifeTimeStartCount, OneYearStartCount, TwoYearStartCount, \
    HasFewStartsInTwoYears
from SampleExtraction.Extractors.time_based import MonthCosExtractor, WeekDaySinExtractor, MonthSinExtractor, \
    WeekDayCosExtractor, HourCosExtractor, HourSinExtractor, AbsoluteTime, MinuteCosExtractor, MinuteSinExtractor
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, SireWinRate, OwnerWinRate, HorseWinRate, \
    JockeyWinRate, HorseJockeyWinRate, HorseBreederWinRate, HorseTrainerWinRate, TrainerWinRate, DamWinRate, \
    DamSireWinRate, JockeyDistanceWinRate, JockeySurfaceWinRate, TrainerDistanceWinRate, TrainerSurfaceWinRate, \
    JockeyTrackWinRate, TrainerTrackWinRate


class FeatureManager:

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features

        self.base_features = [
            CurrentOdds(),
            CurrentSpeedFigure(),

            MonthCosExtractor(), MonthSinExtractor(),
            WeekDayCosExtractor(), WeekDaySinExtractor(),
            HourCosExtractor(), HourSinExtractor(),
            MinuteCosExtractor(), MinuteSinExtractor(),

            CurrentDistance(), CurrentRaceClass(), CurrentGoing(), CurrentRaceTrack(),
            CurrentRaceSurface(), CurrentRaceType(), CurrentRaceTypeDetail(), CurrentRaceCategory(),
        ]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        self.feature_names = [feature.get_name() for feature in self.features]
        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        default_features = [
            Age(), CurrentRating(), DrawBias(),
            HasTrainerMultipleHorses(),
            HasBlinker(),

            AbsoluteTime(),

            HasOptimalBreak(),
            HasLongBreak(),
            HasVeryLongBreak(),
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

            JockeyDistanceWinRate(), JockeySurfaceWinRate(), JockeyTrackWinRate(),
            TrainerDistanceWinRate(), TrainerSurfaceWinRate(), TrainerTrackWinRate(),

            DistanceDifference(), RaceClassDifference(), HasJockeyChanged(),

            PurseExtractor(),
            AveragePlaceLifetimeExtractor(),
            AveragePlaceTrackExtractor(),

            JockeyWeight(),
            MaxPastRatingExtractor(),
            WeightAllowanceExtractor(),
            AveragePlaceSurfaceExtractor(),
        ]

        return default_features

    def warmup_feature_sources(self, race_cards: List[RaceCard]):
        feature_sources = get_feature_sources()
        print(f"Feature sources: {feature_sources}")
        for feature_source in feature_sources:
            feature_source.warmup(race_cards)

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

        feature_sources = get_feature_sources()
        for feature_source in feature_sources:
            feature_source.update(race_card)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
