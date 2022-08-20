from typing import List

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.AverageEarningsJockeyExtractor import AverageEarningsJockeyExtractor
from SampleExtraction.Extractors.AverageEarningsTrainerExtractor import AverageEarningsTrainerExtractor
from SampleExtraction.Extractors.AveragePlaceCategoryExtractor import AveragePlaceCategoryExtractor
from SampleExtraction.Extractors.AveragePlaceLifetime import AveragePlaceLifetimeExtractor
from SampleExtraction.Extractors.AveragePlaceSimilarDistanceExtractor import AveragePlaceSimilarDistanceExtractor
from SampleExtraction.Extractors.AveragePlaceSurfaceExtractor import AveragePlaceSurfaceExtractor
from SampleExtraction.Extractors.AveragePlaceTrackExtractor import AveragePlaceTrackExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.HeadToHeadExtractor import HeadToHeadExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.PastDrawBiasExtractor import PastDrawBiasExtractor
from SampleExtraction.Extractors.PredictedPlaceDeviationExtractor import PredictedPlaceDeviationExtractor
from SampleExtraction.Extractors.PastClassExtractor import PastClassExtractor
from SampleExtraction.Extractors.PastOddsExtractor import PastOddsExtractor
from SampleExtraction.Extractors.PastRatingExtractor import PastRatingExtractor
from SampleExtraction.Extractors.DeviationSpeedFigureExtractor import DeviationSpeedFigureExtractor
from SampleExtraction.Extractors.DistanceDifferenceExtractor import DistanceDifferenceExtractor
from SampleExtraction.Extractors.DrawBiasExtractor import DrawBiasExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.Extractors.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.MaxSpeedFigureExtractor import MaxSpeedFigureExtractor
from SampleExtraction.Extractors.PastPlacesExtractor import PastPlacesExtractor
from SampleExtraction.Extractors.PastRaceCountExtractor import PastRaceCountExtractor
from SampleExtraction.Extractors.SpeedFigureExtractor import SpeedFigureExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.JockeyWeightExtractor import JockeyWeightExtractor
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

        self.n_features = len(self.features)

    def __init_features(self):
        self.__init_past_form_features()
        self.__init_non_past_form_features()

        flattened_past_form_features = [
            past_form_feature for past_form_group in self.past_form_features for past_form_feature in past_form_group
        ]
        self.available_features = flattened_past_form_features + self.non_past_form_features

    def __init_past_form_features(self):
        # Covariate shift:
        self.past_form_features = [[SpeedFigureExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]]
        self.past_form_features.append([LayoffExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)])
        self.past_form_features.append([PastRatingExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)])
        self.past_form_features.append([PastDrawBiasExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)])
        self.past_form_features.append([PastOddsExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)])

        # No covariate shift:
        self.past_form_features.append([PastClassExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)])

    def __init_non_past_form_features(self):
        self.non_past_form_features = [
            # No covariate shift:
            CurrentOddsExtractor(),
            TrackExtractor(),
            DeviationSpeedFigureExtractor(),
            PastRaceCountExtractor(),
            PurseExtractor(),
            MaxSpeedFigureExtractor(),
            DistanceDifferenceExtractor(),
            AveragePlaceLifetimeExtractor(),
            AveragePlaceCategoryExtractor(),
            AveragePlaceTrackExtractor(),

            HeadToHeadExtractor(),

            ColtExtractor(),
            BlinkerExtractor(),

            PredictedPlaceDeviationExtractor(n_races_ago=1),
            PredictedPlaceDeviationExtractor(n_races_ago=2),

            # Covariate Shift:
            DrawBiasExtractor(),
            AgeExtractor(),
            WinRateLifetimeExtractor(),
            JockeyWeightExtractor(),
            GeldingExtractor(),
            MareExtractor(),
            MaxPastRatingExtractor(),
            WeightAllowanceExtractor(),
            AveragePlaceSurfaceExtractor(),

            # Not implemented:
            # JockeyCurrentHorsePurseExtractor(),
            # PreviousRaceStarterCountExtractor(),
            # TrackGoingDifferenceExtractor(),
            # TrackPurseExtractor(),
        ]

        self.non_past_form_features += self.__get_past_race_cards_extractors()

        self.non_past_form_features += [
            PastPlacesExtractor(n_races_ago) for n_races_ago in range(1, 6)
        ]

        # Covariate shift:
        self.non_past_form_features += [
            AveragePlaceSimilarDistanceExtractor(similarity_distance) for similarity_distance in [100, 250, 500, 1000]
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

    def fit_enabled_container(self, race_cards: List[RaceCard]):
        feature_containers = [feature_extractor.container for feature_extractor in self.features]
        for feature_container in feature_containers:
            feature_container.fit(race_cards)

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

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
