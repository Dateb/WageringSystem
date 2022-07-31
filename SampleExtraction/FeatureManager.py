from typing import List, Set

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
from SampleExtraction.Extractors.WeightAllowanceExtractor import WeightAllowanceExtractor
from SampleExtraction.Extractors.WinRateJockeyExtractor import WinRateJockeyExtractor
from SampleExtraction.Extractors.WinRateLifetimeExtractor import WinRateLifetimeExtractor
from SampleExtraction.Extractors.WinRateTrainerExtractor import WinRateTrainerExtractor
from DataAbstraction.Present.Horse import Horse


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

    PAST_PLACES_EXTRACTORS = [PastPlacesExtractor(n_races_ago) for n_races_ago in range(1, 6)]

    # Past form based extractors:
    SPEED_FIGURE_EXTRACTORS = [SpeedFigureExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
    LAYOFF_EXTRACTORS = [LayoffExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
    RATING_EXTRACTORS = [PastRatingExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
    ODDS_EXTRACTORS = [PastOddsExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
    CLASS_EXTRACTORS = [PastClassExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]
    DRAW_BIAS_EXTRACTORS = [PastDrawBiasExtractor(n_races_ago=n_races_ago) for n_races_ago in range(1, 11)]

    ENABLED_FEATURE_EXTRACTORS: List[FeatureExtractor] = SPEED_FIGURE_EXTRACTORS + ODDS_EXTRACTORS + LAYOFF_EXTRACTORS + RATING_EXTRACTORS + CLASS_EXTRACTORS + DRAW_BIAS_EXTRACTORS +  [
        CurrentOddsExtractor(),
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
    ] + PAST_PLACES_EXTRACTORS + AVERAGE_PLACE_SIMILAR_DISTANCE_EXTRACTOR + WIN_RATE_JOCKEY_EXTRACTORS + AVERAGE_EARNINGS_JOCKEY_EXTRACTORS + AVERAGE_EARNINGS_TRAINER_EXTRACTORS + WIN_RATE_TRAINER_EXTRACTORS

    PAST_FORM_FEATURE_NAMES: List[str] = list({
        feature.base_name for feature in ENABLED_FEATURE_EXTRACTORS if feature.base_name != "default"
    })
    NON_PARAMETERIZED_FEATURE_NAMES = [
        feature.get_name() for feature in ENABLED_FEATURE_EXTRACTORS if feature.base_name == "default"
    ]
    FEATURE_NAMES: List[str] = PAST_FORM_FEATURE_NAMES + NON_PARAMETERIZED_FEATURE_NAMES
    FEATURE_COUNT: int = len(ENABLED_FEATURE_EXTRACTORS)

    def fit_enabled_container(self, race_cards: List[RaceCard]):
        feature_containers = [feature_extractor.container for feature_extractor in self.ENABLED_FEATURE_EXTRACTORS]
        for feature_container in feature_containers:
            feature_container.fit(race_cards)

    def set_features(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.__set_features_of_race_card(race_card)

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.ENABLED_FEATURE_EXTRACTORS:
                feature_value = feature_extractor.get_value(race_card, horse)
                if self.__report_missing_features:
                    self.__report_if_feature_missing(horse, feature_extractor, feature_value)
                horse.set_feature_value(feature_extractor.get_name(), feature_value)

    def __report_if_feature_missing(self, horse: Horse, feature_extractor: FeatureExtractor, feature_value):
        if feature_value == feature_extractor.PLACEHOLDER_VALUE:
            horse_name = horse.get_race(0).get_name_of_horse(horse.horse_id)
            print(f"WARNING: Missing feature {feature_extractor.get_name()} for horse {horse_name}, "
                  f"used value: {feature_extractor.PLACEHOLDER_VALUE}")


