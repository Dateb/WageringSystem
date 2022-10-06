from statistics import mean
from typing import List

from numpy import std

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from util.average_calculator import get_simple_average


class FeatureScorer:

    def __init__(self):
        self.scores = []
        self.average_score = 0
        self.std_score = 0

        self.features = {}

    def update_feature_scores(self, score: float, features: List[FeatureExtractor]):
        self.scores.append(score)
        self.average_score = mean(self.scores)
        self.std_score = std(self.scores)

        for feature in features:
            if feature.get_name() in self.features:
                self.features[feature.get_name()]["count"] += 1
                feature_average = self.features[feature.get_name()]["avg"]
                feature_count = self.features[feature.get_name()]["count"]

                new_feature_average = get_simple_average(feature_count, feature_average, score)
                self.features[feature.get_name()]["avg"] = new_feature_average

                self.features[feature.get_name()]["score"] = new_feature_average

            else:
                self.features[feature.get_name()] = {}
                self.features[feature.get_name()]["count"] = 1
                self.features[feature.get_name()]["avg"] = score
                self.features[feature.get_name()]["score"] = score

    def show_feature_scores(self):
        avg_lower = self.average_score - self.std_score
        avg_upper = self.average_score + self.std_score
        print(f"[Average - 1std, Average, Average + 1std] scores: [{avg_lower}, {self.average_score}, {avg_upper}]")
        print("Feature scores:")
        print("---------------------------------")
        for feature in self.features:
            if self.features[feature]["count"] >= 10:
                feature_score = self.features[feature]["score"]
                feature_count = self.features[feature]["count"]
                print(f"{feature} (score / count): {feature_score} / {feature_count}")
        print("---------------------------------")
