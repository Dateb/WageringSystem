from typing import List

from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.AverageEarningsJockeyExtractor import AverageEarningsJockeyExtractor
from SampleExtraction.Extractors.AverageEarningsTrainerExtractor import AverageEarningsTrainerExtractor
from SampleExtraction.Extractors.AveragePlaceLifetime import AveragePlaceLifetimeExtractor
from SampleExtraction.Extractors.AveragePlaceSimilarDistanceExtractor import AveragePlaceSimilarDistanceExtractor
from SampleExtraction.Extractors.AveragePlaceSurfaceExtractor import AveragePlaceSurfaceExtractor
from SampleExtraction.Extractors.AveragePlaceTrackExtractor import AveragePlaceTrackExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.Extractors.HeadToHeadExtractor import HeadToHeadExtractor
from SampleExtraction.Extractors.JockeyCurrentHorsePurseExtractor import JockeyCurrentHorsePurseExtractor
from SampleExtraction.Extractors.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.ParTimeDeviationSameTrack import ParTimeDeviationSameTrack
from SampleExtraction.Extractors.PastAverageHorseDistance import PastAverageHorseDistanceExtractor
from SampleExtraction.Extractors.PastMaxSpeedSameGoingExtractor import PastMaxSpeedSameGoingExtractor
from SampleExtraction.Extractors.PastMaxSpeedSameTrackExtractor import PastMaxSpeedSameTrackExtractor
from SampleExtraction.Extractors.PastMaxSpeedSimilarDistanceExtractor import PastMaxSpeedSimilarDistanceExtractor
from SampleExtraction.Extractors.PastPlacesExtractor import PastPlacesExtractor
from SampleExtraction.Extractors.PastRaceCountExtractor import PastRaceCountExtractor
from SampleExtraction.Extractors.PostPositionExtractor import PostPositionExtractor
from SampleExtraction.Extractors.PredictedPlaceDeviationExtractor import PredictedPlaceDeviationExtractor
from SampleExtraction.Extractors.PreviousClassExtractor import PreviousClassExtractor
from SampleExtraction.Extractors.PreviousHorseDistanceExtractor import PreviousHorseDistanceExtractor
from SampleExtraction.Extractors.PreviousOddsExtractor import PreviousOddsExtractor
from SampleExtraction.Extractors.AverageParTimeDeviationExtractor import AverageParTimeDeviationExtractor
from SampleExtraction.Extractors.PreviousRaceStarterCountExtractor import PreviousRaceStarterCountExtractor
from SampleExtraction.Extractors.DistanceDifferenceExtractor import DistanceDifferenceExtractor
from SampleExtraction.Extractors.PreviousSpeedExtractor import PreviousSpeedExtractor
from SampleExtraction.Extractors.AverageSpeedFigureExtractor import AverageSpeedFigureExtractor
from SampleExtraction.Extractors.TrackPurseExtractor import TrackPurseExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.AverageRatingExtractor import AverageRatingExtractor
from SampleExtraction.Extractors.TrackGoingDifferenceExtractor import TrackGoingDifferenceExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WeightDifferenceExtractor import WeightDifferenceExtractor
from SampleExtraction.Extractors.WeightJockeyExtractor import WeightJockeyExtractor
from SampleExtraction.Extractors.AveragePlaceCategoryExtractor import AveragePlaceCategoryExtractor
from SampleExtraction.Extractors.WinRateJockeyExtractor import WinRateJockeyExtractor
from SampleExtraction.Extractors.WinRateLifetimeExtractor import WinRateLifetimeExtractor
from SampleExtraction.Extractors.WinRateTrainerExtractor import WinRateTrainerExtractor
from SampleExtraction.Horse import Horse


class FeatureManager:

    def __init__(self, report_missing_features: bool = False):
        self.__report_missing_features = report_missing_features

    AVERAGE_EARNINGS_JOCKEY_EXTRACTORS = [AverageEarningsJockeyExtractor(race_card_idx) for race_card_idx in range(3)]
    AVERAGE_EARNINGS_TRAINER_EXTRACTORS = [AverageEarningsTrainerExtractor(race_card_idx) for race_card_idx in range(3)]

    WIN_RATE_JOCKEY_EXTRACTORS = [WinRateJockeyExtractor(race_card_idx) for race_card_idx in range(3)]
    WIN_RATE_TRAINER_EXTRACTORS = [WinRateTrainerExtractor(race_card_idx) for race_card_idx in range(3)]

    AVERAGE_PLACE_SIMILAR_DISTANCE_EXTRACTOR = [
        AveragePlaceSimilarDistanceExtractor(similarity_distance) for similarity_distance in [100, 250, 500, 1000]
    ]

    POST_POSITION_EXTRACTORS = [PostPositionExtractor(race_card_idx) for race_card_idx in range(3)]

    PAST_PLACES_EXTRACTORS = [PastPlacesExtractor(n_races_ago) for n_races_ago in range(1, 6)]

    ENABLED_FEATURE_EXTRACTORS: List[FeatureExtractor] = [
        CurrentOddsExtractor(),
        AverageSpeedFigureExtractor(),

        AverageRatingExtractor(n_races_ago=5),
        PreviousSpeedExtractor(),
        PastMaxSpeedSimilarDistanceExtractor(),
        PastMaxSpeedSameTrackExtractor(),
        PastMaxSpeedSameGoingExtractor(),
        LayoffExtractor(),

        # PredictedPlaceDeviationExtractor(n_races_ago=1),
        # PredictedPlaceDeviationExtractor(n_races_ago=2),

        AveragePlaceLifetimeExtractor(),
        WinRateLifetimeExtractor(),
        AgeExtractor(),
        AveragePlaceCategoryExtractor(),
        AveragePlaceSurfaceExtractor(),
        AveragePlaceTrackExtractor(),
        DistanceDifferenceExtractor(),
        HeadToHeadExtractor(),
        BlinkerExtractor(),
        ColtExtractor(),
        GeldingExtractor(),
        MareExtractor(),
        JockeyCurrentHorsePurseExtractor(),
        MaxPastRatingExtractor(),
        PastAverageHorseDistanceExtractor(),
        PastRaceCountExtractor(),
        PreviousClassExtractor(),
        PreviousHorseDistanceExtractor(),
        PreviousOddsExtractor(),
        PreviousRaceStarterCountExtractor(),
        PurseExtractor(),
        TrackGoingDifferenceExtractor(),
        TrackPurseExtractor(),
        WeightAllowanceExtractor(),
        WeightDifferenceExtractor(),
        WeightJockeyExtractor(),
    ]# + AVERAGE_EARNINGS_JOCKEY_EXTRACTORS + AVERAGE_EARNINGS_TRAINER_EXTRACTORS + PAST_PLACES_EXTRACTORS + WIN_RATE_JOCKEY_EXTRACTORS + WIN_RATE_TRAINER_EXTRACTORS + POST_POSITION_EXTRACTORS + AVERAGE_PLACE_SIMILAR_DISTANCE_EXTRACTOR

    FEATURE_NAMES: List[str] = [feature.get_name() for feature in ENABLED_FEATURE_EXTRACTORS]

    def set_features_of_horse(self, horse: Horse) -> None:
        for feature_extractor in self.ENABLED_FEATURE_EXTRACTORS:
            feature_value = feature_extractor.get_value(horse)
            if self.__report_missing_features:
                self.__report_if_feature_missing(horse, feature_extractor, feature_value)
            horse.set_feature(feature_extractor.get_name(), feature_value)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")


