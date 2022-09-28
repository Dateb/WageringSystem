from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.AveragePlaceLifetime import AveragePlaceLifetimeExtractor
from SampleExtraction.Extractors.AveragePlaceSurfaceExtractor import AveragePlaceSurfaceExtractor
from SampleExtraction.Extractors.AveragePlaceTrackExtractor import AveragePlaceTrackExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.DrawBiasExtractor import DrawBiasExtractor
from SampleExtraction.Extractors.Form_Based.PastDistanceExtractor import PastDistanceExtractor
from SampleExtraction.Extractors.Form_Based.PastDrawBiasExtractor import PastDrawBiasExtractor
from SampleExtraction.Extractors.Form_Based.PastFasterHorsesExtractor import PastFasterHorsesExtractor
from SampleExtraction.Extractors.Form_Based.PastSlowerHorsesExtractor import PastSlowerHorsesExtractor
from SampleExtraction.Extractors.HeadToHeadExtractor import HeadToHeadExtractor
from SampleExtraction.Extractors.current_race_based import CurrentOdds, Age, HasTrainerMultipleHorses, CurrentDistance, \
    CurrentRaceClass, CurrentGoing
from SampleExtraction.Extractors.gender_based import IsGelding, IsMare, IsColt
from SampleExtraction.Extractors.layoff_based import HasOptimalBreak, HasLongBreak, \
    HasVeryLongBreak, HasWonAfterLongBreak
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.Form_Based.PastGoingExtractor import PastGoingExtractor
from SampleExtraction.Extractors.PastLengthsBehindWinnerExtractor import PastLengthsBehindWinnerExtractor
from SampleExtraction.Extractors.Form_Based.PastWeightExtractor import PastWeightExtractor
from SampleExtraction.Extractors.Form_Based.PastClassExtractor import PastClassExtractor
from SampleExtraction.Extractors.Form_Based.PastOddsExtractor import PastOddsExtractor
from SampleExtraction.Extractors.Form_Based.PastRatingExtractor import PastRatingExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.Form_Based.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.JockeyWeightExtractor import JockeyWeightExtractor
from SampleExtraction.Extractors.TrackExtractor import TrackExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from DataAbstraction.Present.Horse import Horse
from SampleExtraction.Extractors.odds_based import HighestOddsWin
from SampleExtraction.Extractors.previous_race_difference_based import DistanceDifference, RaceClassDifference
from SampleExtraction.Extractors.speed_based import CurrentSpeedFigure
from SampleExtraction.Extractors.starts_based import LifeTimeStartCount, OneYearStartCount, TwoYearStartCount, \
    HasFewStartsInTwoYears
from SampleExtraction.Extractors.time_based import MonthCosExtractor, WeekDaySinExtractor, MonthSinExtractor, \
    WeekDayCosExtractor, HourCosExtractor, HourSinExtractor
from SampleExtraction.Extractors.win_rate_based import BreederWinRate, SireWinRate, OwnerWinRate, HorseWinRate, \
    JockeyWinRate


class FeatureManager:

    def __init__(
            self,
            report_missing_features: bool = False,
            features: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features
        self.features = features
        self.__init_features()
        if features is None:
            self.features = self.available_features

        self.feature_names = [feature.get_name() for feature in self.features]
        self.n_features = len(self.features)

    def __init_features(self):
        #self.__init_past_form_features()
        self.__init_non_past_form_features()

        # flattened_past_form_features = [
        #     past_form_feature for past_form_group in self.past_form_features for past_form_feature in past_form_group
        # ]
        self.available_features = self.non_past_form_features

    def __init_past_form_features(self):
        past_form_depth = 11
        # Covariate shift:
        self.past_form_features = [[LayoffExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)]]
        self.past_form_features.append([PastDrawBiasExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])

        self.past_form_features.append([PastRatingExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastOddsExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])

        # No covariate shift:
        self.past_form_features.append([PastClassExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])

        # Unknown
        self.past_form_features.append([PastSlowerHorsesExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastFasterHorsesExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastDistanceExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastWeightExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastLengthsBehindWinnerExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
        self.past_form_features.append([PastGoingExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])

    def __init_non_past_form_features(self):
        self.non_past_form_features = [
            CurrentOdds(), CurrentDistance(), CurrentRaceClass(), CurrentGoing(),

            MonthCosExtractor(), MonthSinExtractor(),
            WeekDayCosExtractor(), WeekDaySinExtractor(),
            HourCosExtractor(), HourSinExtractor(),

            Age(),
            DrawBiasExtractor(),
            HasTrainerMultipleHorses(),
            TrackExtractor(),

            CurrentSpeedFigure(),

            HasOptimalBreak(),
            HasLongBreak(),
            HasVeryLongBreak(),
            HasWonAfterLongBreak(),

            LifeTimeStartCount(),
            OneYearStartCount(),
            TwoYearStartCount(),
            HasFewStartsInTwoYears(),

            HighestOddsWin(),

            IsGelding(), IsMare(), IsColt(),

            HorseWinRate(), JockeyWinRate(),
            BreederWinRate(), OwnerWinRate(),
            SireWinRate(),

            DistanceDifference(), RaceClassDifference(),

            PurseExtractor(),
            AveragePlaceLifetimeExtractor(),
            AveragePlaceTrackExtractor(),

            HeadToHeadExtractor(),

            BlinkerExtractor(),

            # PredictedPlaceDeviationExtractor(n_races_ago=1),
            # PredictedPlaceDeviationExtractor(n_races_ago=2),

            # Covariate Shift:
            JockeyWeightExtractor(),
            MaxPastRatingExtractor(),
            WeightAllowanceExtractor(),
            AveragePlaceSurfaceExtractor(),

            # Not implemented:
            # JockeyCurrentHorsePurseExtractor(),
            # PreviousRaceStarterCountExtractor(),
            # TrackGoingDifferenceExtractor(),
            # TrackPurseExtractor(),
        ]

        # self.non_past_form_features += self.__get_past_race_cards_extractors()
        #
        # self.non_past_form_features += [
        #     PastPlacesExtractor(n_races_ago) for n_races_ago in range(1, 6)
        # ]

    def warmup_feature_sources(self, race_cards: List[RaceCard]):
        feature_sources = {feature_extractor.source for feature_extractor in self.features}
        print(f"Feature sources: {feature_sources}")
        for feature_source in feature_sources:
            feature_source.warmup(race_cards)

    def set_features(self, race_cards: Dict[str, RaceCard]):
        for datetime in sorted(race_cards):
            self.__set_features_of_race_card(race_cards[datetime])

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.features:
                feature_value = feature_extractor.get_value(race_card, horse)
                if self.__report_missing_features:
                    self.__report_if_feature_missing(horse, feature_extractor, feature_value)
                horse.set_feature_value(feature_extractor.get_name(), feature_value)

        feature_sources = {feature_extractor.source for feature_extractor in self.features}
        for feature_source in feature_sources:
            feature_source.update(race_card)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
