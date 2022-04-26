from typing import List

from SampleExtraction.Extractors.AgeExtractor import AgeExtractor
from SampleExtraction.Extractors.BlinkerExtractor import BlinkerExtractor
from SampleExtraction.Extractors.ColtExtractor import ColtExtractor
from SampleExtraction.Extractors.EarningsJockeyExtractor import EarningsJockeyExtractor
from SampleExtraction.Extractors.EarningsTrainerExtractor import EarningsTrainerExtractor
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.Extractors.GeldingExtractor import GeldingExtractor
from SampleExtraction.Extractors.InitialOddsExtractor import InitialOddsExtractor
from SampleExtraction.Extractors.MareExtractor import MareExtractor
from SampleExtraction.Extractors.NumPlaceJockeyExtractor import NumPlaceJockeyExtractor
from SampleExtraction.Extractors.NumPlaceTrainerExtractor import NumPlaceTrainerExtractor
from SampleExtraction.Extractors.NumRacesJockeyExtractor import NumRacesJockeyExtractor
from SampleExtraction.Extractors.NumRacesTrainerExtractor import NumRacesTrainerExtractor
from SampleExtraction.Extractors.NumWinsJockeyExtractor import NumWinsJockeyExtractor
from SampleExtraction.Extractors.NumWinsTrainerExtractor import NumWinsTrainerExtractor
from SampleExtraction.Extractors.PastPlacesExtractor import PastPlacesExtractor
from SampleExtraction.Extractors.PostPositionExtractor import PostPositionExtractor
from SampleExtraction.Extractors.PurseExtractor import PurseExtractor
from SampleExtraction.Extractors.RatingExtractor import RatingExtractor
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WeightJockeyExtractor import WeightJockeyExtractor


class FeatureManager:

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
    ]
    FEATURE_NAMES: List[str] = [feature.get_name() for feature in ENABLED_FEATURE_EXTRACTORS]

