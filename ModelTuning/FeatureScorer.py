from dataclasses import dataclass
from statistics import mean
from typing import List, Dict

from numpy import std

from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from util.stats_calculator import SimpleOnlineCalculator


@dataclass
class FeatureScore:

    score: float
    goodness: float
    count: int

    def __gt__(self, other_feature_score) -> bool:
        return self.goodness > other_feature_score.goodness


class FeatureScorer:

    def __init__(self, search_features: List[FeatureExtractor], report_interval: int = 5):
        self.scores = []
        self.average_score = 0
        self.std_score = 0

        self.feature_scores: Dict[str, FeatureScore] = {
            feature.get_name(): FeatureScore(0, 0, 0) for feature in search_features
        }
        self.report_interval = report_interval
        self.n_updates = 0

    def update_feature_scores(self, score: float, features: List[FeatureExtractor]):
        self.n_updates += 1
        self.scores.append(score)
        self.average_score = mean(self.scores)
        self.std_score = std(self.scores)

        for feature in features:
            feature_name = feature.get_name()
            if feature_name in self.feature_scores:
                self.feature_scores[feature_name].count += 1

                feature_score = self.feature_scores[feature_name].score
                feature_count = self.feature_scores[feature_name].count
                new_feature_score = SimpleOnlineCalculator().calculate_average(
                    feature_score,
                    0
                )

                self.feature_scores[feature_name].score = new_feature_score
                self.feature_scores[feature_name].goodness = (new_feature_score - self.average_score) / self.std_score

        if self.n_updates % self.report_interval == 0:
            self.show_feature_scores()

    def show_feature_scores(self):
        avg_lower = self.average_score - self.std_score
        avg_upper = self.average_score + self.std_score
        print(f"[Average - 1std, Average, Average + 1std] scores: [{avg_lower}, {self.average_score}, {avg_upper}]")
        print("Feature scores:")
        print("---------------------------------")
        self.feature_scores = {feature_name: feature_score for feature_name, feature_score in sorted(self.feature_scores.items(), key=lambda item: item[1])}
        for feature_name, feature_score in self.feature_scores.items():
            if feature_score.count >= 10:
                print(f"{feature_name} goodness: {feature_score.goodness}")
        print("---------------------------------")
