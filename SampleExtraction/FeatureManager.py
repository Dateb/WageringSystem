import pickle
from typing import List

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor, FeatureSourceExtractor, LayoffExtractor
from SampleExtraction.Extractors.horse_attributes_based import Age, Gender, Origin
from SampleExtraction.Extractors.jockey_based import CurrentJockeyWeight
from SampleExtraction.feature_sources.feature_sources import PreviousSource, FeatureValueGroup
from util.nested_dict import nested_dict
from util.stats_calculator import SimpleOnlineCalculator


class FeatureManager:

    def __init__(self, features: List[FeatureExtractor] = None):
        self.base_features = [
            # HasWon(),

            # IsFavorite(),
            # IndustryMarketWinProbabilityDiff(),
            #
            # BetfairOverround(),
            # IsSecondRaceForJockey(),

            # RacebetsWinProbability(),
            # BetfairPlaceMarketWinProbability(),

            # BaseTime(),
        ]

        self.previous_value_source = PreviousSource()

        self.feature_sources = [self.previous_value_source]

        self.features = features
        if features is None:
            self.search_features = self.get_search_features()
            self.features = self.base_features + self.search_features

        # TODO: The construction of self.feature_names is sensible to ordering. The usage should be more robust
        self.feature_names = [feature.name for feature in self.features]
        self.numerical_feature_names = [feature.name for feature in self.features if not feature.is_categorical]
        self.categorical_feature_names = [feature.name for feature in self.features if feature.is_categorical]

        self.n_features = len(self.features)

    def get_search_features(self) -> List[FeatureExtractor]:
        features = []

        with open('../SampleExtraction/features.pkl', 'rb') as f:
            feature_data = pickle.load(f)

        for feature_source, feature_value_calculators in feature_data.items():
            self.feature_sources.append(feature_source)
            for feature_value_calculator, attribute_groups in feature_value_calculators.items():
                for attribute_group in attribute_groups:
                    horse_attributes = attribute_group[0]
                    race_attributes = attribute_group[1]
                    feature_value_group = FeatureValueGroup(feature_value_calculator, horse_attributes, race_attributes)
                    features.append(FeatureSourceExtractor(feature_source, feature_value_group))

        print(features)

        current_race_features = [
            Age(),
            Gender(),
            Origin(),
            CurrentJockeyWeight(),
        ]

        self.feature_value_groups = []
        for feature_source in self.feature_sources:
            for feature_value_group in feature_source.feature_value_groups:
                if feature_value_group not in self.feature_value_groups:
                    self.feature_value_groups.append(feature_value_group)

        self.feature_value_group_to_source_map = {feature_value_group: [] for feature_value_group in
                                                  self.feature_value_groups}
        for feature_source in self.feature_sources:
            for feature_value_group in feature_source.feature_value_groups:
                self.feature_value_group_to_source_map[feature_value_group].append(feature_source)

        return features + current_race_features

    def set_features(self, race_cards: List[RaceCard]):
        for race_card in race_cards:
            self.__set_features_of_race_card(race_card)

    def __set_features_of_race_card(self, race_card: RaceCard):
        for horse in race_card.horses:
            for feature_extractor in self.features:
                feature_value = feature_extractor.get_value(race_card, horse)
                horse.set_feature_value(feature_extractor.name, feature_value)

    def pre_update_feature_sources(self, race_card: RaceCard) -> None:
        for feature_source in self.feature_sources:
            for horse in race_card.runners:
                feature_source.pre_update(race_card, horse)

    def post_update_feature_sources(self, race_cards: List[RaceCard]) -> None:
        race_cards = [race_card for race_card in race_cards if
                      race_card.has_results and race_card.feature_source_validity]

        current_date = None
        for feature_value_group in self.feature_value_groups:
            feature_values = nested_dict()
            for race_card in race_cards:
                current_date = race_card.date
                if race_card.is_valid_sample:
                    race_card_key = feature_value_group.race_card_key_cache[race_card.race_id]
                else:
                    race_card_key = feature_value_group.get_race_card_key(race_card)
                for horse in race_card.horses:
                    if not horse.is_nonrunner:
                        if race_card.is_valid_sample:
                            feature_value_group_key = feature_value_group.key_cache[horse.subject_id]
                        else:
                            feature_value_group_key = feature_value_group.get_key(race_card_key, horse)
                        new_feature_value = feature_value_group.value_calculator.calculate(race_card, horse)
                        if new_feature_value is not None:
                            if isinstance(new_feature_value, float):
                                if feature_value_group_key not in feature_values:
                                    feature_values[feature_value_group_key]["count"] = 1
                                    feature_values[feature_value_group_key]["avg"] = new_feature_value
                                else:
                                    feature_values[feature_value_group_key]["count"] += 1
                                    feature_values[feature_value_group_key]["avg"] = SimpleOnlineCalculator().calculate_average(
                                        old_average=feature_values[feature_value_group_key]["avg"],
                                        new_obs=new_feature_value,
                                        n_days_since_last_obs=0,
                                        count=feature_values[feature_value_group_key]["count"]
                                    )
                            else:
                                feature_values[feature_value_group_key]["avg"] = new_feature_value

            for feature_source in self.feature_value_group_to_source_map[feature_value_group]:
                if not feature_value_group.value_calculator.is_available_before_race:
                    feature_source.post_update(race_cards, feature_values, current_date)

        for feature_value_group in self.feature_value_groups:
            feature_value_group.clear_cache()
