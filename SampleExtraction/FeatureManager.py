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
            feature_extractors: List[FeatureExtractor] = None
    ):
        self.__report_missing_features = report_missing_features
        self.feature_extractors = feature_extractors
        if feature_extractors is None:
            self.__init_feature_extractors()

        self.past_form_feature_names = list({
            feature.base_name for feature in self.feature_extractors if feature.base_name != "default"
        })
        self.non_parameterized_feature_names = [
            feature.get_name() for feature in self.feature_extractors if feature.base_name == "default"
        ]

        self.feature_names = self.past_form_feature_names + self.non_parameterized_feature_names
        self.n_features = len(self.feature_extractors)

    def __init_feature_extractors(self):
        self.feature_extractors = [
            CurrentOddsExtractor(),
            TrackExtractor(),
            DeviationSpeedFigureExtractor(),
            MaxSpeedFigureExtractor(),
            AgeExtractor(),
            DrawBiasExtractor(),
            PurseExtractor(),
            PastRaceCountExtractor(),
            JockeyWeightExtractor(),
            WinRateLifetimeExtractor(),
            DistanceDifferenceExtractor(),
            WeightAllowanceExtractor(),
            BlinkerExtractor(),
            AveragePlaceLifetimeExtractor(),

            PredictedPlaceDeviationExtractor(n_races_ago=1),
            PredictedPlaceDeviationExtractor(n_races_ago=2),

            ColtExtractor(),
            GeldingExtractor(),
            MareExtractor(),

            AveragePlaceCategoryExtractor(),
            AveragePlaceSurfaceExtractor(),
            AveragePlaceTrackExtractor(),
            HeadToHeadExtractor(),
            MaxPastRatingExtractor(),
            # JockeyCurrentHorsePurseExtractor(),
            # PreviousRaceStarterCountExtractor(),
            # TrackGoingDifferenceExtractor(),
            # TrackPurseExtractor(),
        ]

        self.feature_extractors += self.__get_past_race_cards_extractors()
        self.feature_extractors += self.__get_past_form_extractors()
        self.feature_extractors += [
            AveragePlaceSimilarDistanceExtractor(similarity_distance) for similarity_distance in [100, 250, 500, 1000]
        ]
        self.feature_extractors += [
            PastPlacesExtractor(n_races_ago) for n_races_ago in range(1, 6)
        ]

    def __get_past_race_cards_extractors(self) -> List[FeatureExtractor]:
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

    def __get_past_form_extractors(self) -> List[FeatureExtractor]:
        past_form_extractors = [SpeedFigureExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
        past_form_extractors += [LayoffExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
        past_form_extractors += [PastRatingExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
        past_form_extractors += [PastOddsExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
        past_form_extractors += [PastClassExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
        past_form_extractors += [PastDrawBiasExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]

        return past_form_extractors

    def fit_enabled_container(self, race_cards: List[RaceCard]):
        feature_containers = [feature_extractor.container for feature_extractor in self.feature_extractors]
        for feature_container in feature_containers:
            feature_container.fit(race_cards)

    def set_features(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.__set_features_of_race_card(race_card)

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.feature_extractors:
                feature_value = feature_extractor.get_value(race_card, horse)
                if self.__report_missing_features:
                    self.__report_if_feature_missing(horse, feature_extractor, feature_value)
                horse.set_feature_value(feature_extractor.get_name(), feature_value)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")
