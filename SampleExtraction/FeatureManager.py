from typing import List

from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.EarningsJockeyExtractor import EarningsJockeyExtractor
from SampleExtraction.Extractors.EarningsTrainerExtractor import EarningsTrainerExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.InitialOddsExtractor import InitialOddsExtractor
from SampleExtraction.Extractors.LayoffExtractor import LayoffExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.NumPlaceJockeyExtractor import NumPlaceJockeyExtractor
from SampleExtraction.Extractors.NumPlaceTrainerExtractor import NumPlaceTrainerExtractor
from SampleExtraction.Extractors.NumRacesJockeyExtractor import NumRacesJockeyExtractor
from SampleExtraction.Extractors.NumRacesTrainerExtractor import NumRacesTrainerExtractor
from SampleExtraction.Extractors.NumWinsJockeyExtractor import NumWinsJockeyExtractor
from SampleExtraction.Extractors.NumWinsTrainerExtractor import NumWinsTrainerExtractor
from SampleExtraction.Extractors.PastPlacesExtractor import PastPlacesExtractor
from SampleExtraction.Extractors.PostPositionExtractor import PostPositionExtractor
from SampleExtraction.Extractors.PreviousOddsExtractor import PreviousOddsExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.RatingExtractor import RatingExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WeightJockeyExtractor import WeightJockeyExtractor
from SampleExtraction.Horse import Horse


class FeatureManager:

    def __init__(self, report_missing_features: bool = False):
        self.__report_missing_features = report_missing_features

    ENABLED_FEATURE_EXTRACTORS: List[FeatureExtractor] = [
        AgeExtractor(),
        RatingExtractor(),
        WeightAllowanceExtractor(),
        BlinkerExtractor(),

        ColtExtractor(),
        GeldingExtractor(),
        MareExtractor(),

        InitialOddsExtractor(),
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
        PostPositionExtractor(),
        PastPlacesExtractor(1),
        PastPlacesExtractor(2),
        PastPlacesExtractor(3),
        PastPlacesExtractor(4),
        PastPlacesExtractor(5),

        # ---Past performance features---
        LayoffExtractor(),
        PreviousOddsExtractor(),
    ]
    FEATURE_NAMES: List[str] = [feature.get_name() for feature in ENABLED_FEATURE_EXTRACTORS]

    def set_features_of_horse(self, horse: Horse) -> None:
        for feature_extractor in self.ENABLED_FEATURE_EXTRACTORS:
            feature_value = feature_extractor.get_value(horse)
            if self.__report_missing_features:
                self.__report_if_feature_missing(feature_extractor, feature_value)
            horse.set_feature(feature_extractor.get_name(), feature_value)

    def __report_if_feature_missing(self, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            print(f"WARNING: Missing feature {feature_extractor.get_name()}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")


