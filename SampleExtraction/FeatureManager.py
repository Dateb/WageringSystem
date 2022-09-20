from typing import List, Dict

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.AverageEarningsJockeyExtractor import AverageEarningsJockeyExtractor
from SampleExtraction.Extractors.AverageEarningsTrainerExtractor import AverageEarningsTrainerExtractor
from SampleExtraction.Extractors.AveragePlaceCategoryExtractor import AveragePlaceCategoryExtractor
from SampleExtraction.Extractors.AveragePlaceLifetime import AveragePlaceLifetimeExtractor
from SampleExtraction.Extractors.AverageSpeedSimilarDistanceExtractor import AverageSpeedSimilarDistanceExtractor
from SampleExtraction.Extractors.AveragePlaceSurfaceExtractor import AveragePlaceSurfaceExtractor
from SampleExtraction.Extractors.AveragePlaceTrackExtractor import AveragePlaceTrackExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.BreederWinRateExtractor import BreederWinRateExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.DeviationSpeedFigureExtractor import DeviationSpeedFigureExtractor
from SampleExtraction.Extractors.DrawBiasExtractor import DrawBiasExtractor
from SampleExtraction.Extractors.Form_Based.PastDistanceExtractor import PastDistanceExtractor
from SampleExtraction.Extractors.Form_Based.PastDrawBiasExtractor import PastDrawBiasExtractor
from SampleExtraction.Extractors.Form_Based.PastFasterHorsesExtractor import PastFasterHorsesExtractor
from SampleExtraction.Extractors.Form_Based.PastSlowerHorsesExtractor import PastSlowerHorsesExtractor
from SampleExtraction.Extractors.Form_Based.SpeedFigureExtractor import SpeedFigureExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.HeadToHeadExtractor import HeadToHeadExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.Form_Based.PastGoingExtractor import PastGoingExtractor
from SampleExtraction.Extractors.MaxSpeedFigureExtractor import MaxSpeedFigureExtractor
from SampleExtraction.Extractors.Time.HourCosExtractor import HourCosExtractor
from SampleExtraction.Extractors.Time.HourSinExtractor import HourSinExtractor
from SampleExtraction.Extractors.Time.MonthCosExtractor import MonthCosExtractor
from SampleExtraction.Extractors.Time.MonthSinExtractor import MonthSinExtractor
from SampleExtraction.Extractors.OwnerWinRateExtractor import OwnerWinRateExtractor
from SampleExtraction.Extractors.PastLengthsBehindWinnerExtractor import PastLengthsBehindWinnerExtractor
from SampleExtraction.Extractors.Form_Based.PastWeightExtractor import PastWeightExtractor
from SampleExtraction.Extractors.PredictedPlaceDeviationExtractor import PredictedPlaceDeviationExtractor
from SampleExtraction.Extractors.Form_Based.PastClassExtractor import PastClassExtractor
from SampleExtraction.Extractors.Form_Based.PastOddsExtractor import PastOddsExtractor
from SampleExtraction.Extractors.Form_Based.PastRatingExtractor import PastRatingExtractor
from SampleExtraction.Extractors.DistanceDifferenceExtractor import DistanceDifferenceExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.Extractors.Form_Based.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.PastRaceCountExtractor import PastRaceCountExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.JockeyWeightExtractor import JockeyWeightExtractor
from SampleExtraction.Extractors.Time.WeekDayCosExtractor import WeekDayCosExtractor
from SampleExtraction.Extractors.Time.WeekDaySinExtractor import WeekDaySinExtractor
from SampleExtraction.Extractors.TrackExtractor import TrackExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WinRateJockeyExtractor import WinRateJockeyExtractor
from SampleExtraction.Extractors.WinRateLifetimeExtractor import WinRateLifetimeExtractor
from SampleExtraction.Extractors.WinRateTrainerExtractor import WinRateTrainerExtractor
from DataAbstraction.Present.Horse import Horse


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
        self.__init_past_form_features()
        self.__init_non_past_form_features()

        flattened_past_form_features = [
            past_form_feature for past_form_group in self.past_form_features for past_form_feature in past_form_group
        ]
        self.available_features = flattened_past_form_features + self.non_past_form_features

    def __init_past_form_features(self):
        past_form_depth = 11
        # Covariate shift:
        self.past_form_features = [[LayoffExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)]]

        self.past_form_features.append([SpeedFigureExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, past_form_depth)])
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
            # No covariate shift:
            CurrentOddsExtractor(),

            MonthCosExtractor(), MonthSinExtractor(),
            WeekDayCosExtractor(), WeekDaySinExtractor(),
            HourCosExtractor(), HourSinExtractor(),

            BreederWinRateExtractor(),
            OwnerWinRateExtractor(),
            TrackExtractor(),
            PastRaceCountExtractor(),
            PurseExtractor(),
            DistanceDifferenceExtractor(),
            AveragePlaceLifetimeExtractor(),
            AveragePlaceCategoryExtractor(),
            AveragePlaceTrackExtractor(),

            HeadToHeadExtractor(),

            BlinkerExtractor(),

            PredictedPlaceDeviationExtractor(n_races_ago=1),
            # PredictedPlaceDeviationExtractor(n_races_ago=2),

            DeviationSpeedFigureExtractor(),
            MaxSpeedFigureExtractor(),

            # Covariate Shift:
            DrawBiasExtractor(),
            AgeExtractor(),
            WinRateLifetimeExtractor(),
            JockeyWeightExtractor(),
            GeldingExtractor(),
            MareExtractor(),
            ColtExtractor(),
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

        # Covariate shift:
        self.non_past_form_features += [
            AverageSpeedSimilarDistanceExtractor(similarity_distance) for similarity_distance in [100, 250, 500, 1000]
        ]

    def __get_past_race_cards_extractors(self) -> List[FeatureExtractor]:
        # Covariate shift
        past_race_cards_extractors = [
            AverageEarningsJockeyExtractor(race_card_idx) for race_card_idx in range(3)
        ]
        past_race_cards_extractors += [
            AverageEarningsTrainerExtractor(race_card_idx) for race_card_idx in range(3)
        ]
        past_race_cards_extractors += [
            WinRateJockeyExtractor(race_card_idx) for race_card_idx in range(3)
        ]
        past_race_cards_extractors += [
            WinRateTrainerExtractor(race_card_idx) for race_card_idx in range(3)
        ]

        return past_race_cards_extractors

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
