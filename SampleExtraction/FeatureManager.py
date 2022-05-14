from typing import List

from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.AveragePlaceSimilarDistanceExtractor import AveragePlaceSimilarDistanceExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.EarningsJockeyExtractor import EarningsJockeyExtractor
from SampleExtraction.Extractors.EarningsTrainerExtractor import EarningsTrainerExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.CurrentOddsExtractor import CurrentOddsExtractor
from SampleExtraction.Extractors.HeadToHeadExtractor import HeadToHeadExtractor
from SampleExtraction.Extractors.JockeyCurrentHorsePurseExtractor import JockeyCurrentHorsePurseExtractor
from SampleExtraction.Extractors.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.MaxPastRatingExtractor import MaxPastRatingExtractor
from SampleExtraction.Extractors.NumPlaceJockeyExtractor import NumPlaceJockeyExtractor
from SampleExtraction.Extractors.NumPlaceTrainerExtractor import NumPlaceTrainerExtractor
from SampleExtraction.Extractors.NumRacesJockeyExtractor import NumRacesJockeyExtractor
from SampleExtraction.Extractors.NumRacesTrainerExtractor import NumRacesTrainerExtractor
from SampleExtraction.Extractors.NumWinsJockeyExtractor import NumWinsJockeyExtractor
from SampleExtraction.Extractors.NumWinsTrainerExtractor import NumWinsTrainerExtractor
from SampleExtraction.Extractors.PastAverageHorseDistance import PastAverageHorseDistanceExtractor
from SampleExtraction.Extractors.PastPlacesExtractor import PastPlacesExtractor
from SampleExtraction.Extractors.PastRaceCountExtractor import PastRaceCountExtractor
from SampleExtraction.Extractors.PostPositionExtractor import PostPositionExtractor
from SampleExtraction.Extractors.PreviousAveragePurseExtractor import PreviousAveragePurseExtractor
from SampleExtraction.Extractors.PreviousOddsExtractor import PreviousOddsExtractor
from SampleExtraction.Extractors.PreviousRaceStarterCountExtractor import PreviousRaceStarterCountExtractor
from SampleExtraction.Extractors.DistanceDifferenceExtractor import DistanceDifferenceExtractor
from SampleExtraction.Extractors.TrackPurseExtractor import TrackPurseExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.RatingExtractor import RatingExtractor
from SampleExtraction.Extractors.TrackGoingDifferenceExtractor import TrackGoingDifferenceExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WeightDifferenceExtractor import WeightDifferenceExtractor
from SampleExtraction.Extractors.WeightJockeyExtractor import WeightJockeyExtractor
from SampleExtraction.Extractors.AveragePlaceCategoryExtractor import AveragePlaceCategoryExtractor
from SampleExtraction.Horse import Horse


class FeatureManager:

    def __init__(self, report_missing_features: bool = False):
        self.__report_missing_features = report_missing_features

    ENABLED_FEATURE_EXTRACTORS: List[FeatureExtractor] = [
        AgeExtractor(),
        RatingExtractor(),

        #BlinkerExtractor(),
        #ColtExtractor(),
        #GeldingExtractor(),
        #MareExtractor(),
        #WeightAllowanceExtractor(),
        #HeadToHeadExtractor(),

        #CurrentOddsExtractor(),
        NumRacesJockeyExtractor(),
        NumWinsJockeyExtractor(),
        NumPlaceJockeyExtractor(),
        EarningsJockeyExtractor(),
        NumRacesTrainerExtractor(),
        NumPlaceTrainerExtractor(),
        NumWinsTrainerExtractor(),
        EarningsTrainerExtractor(),
        WeightJockeyExtractor(),
        PurseExtractor(),

        # ---Past performance features---
        LayoffExtractor(),
        PreviousOddsExtractor(),
        WeightDifferenceExtractor(),
        PreviousAveragePurseExtractor(),
        PreviousRaceStarterCountExtractor(),
        DistanceDifferenceExtractor(),
        TrackGoingDifferenceExtractor(),

        PastRaceCountExtractor(),
        PastAverageHorseDistanceExtractor(),
        JockeyCurrentHorsePurseExtractor(),
        MaxPastRatingExtractor(),
        TrackPurseExtractor(),
        AveragePlaceCategoryExtractor(),
        AveragePlaceSimilarDistanceExtractor(),
    ]
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


