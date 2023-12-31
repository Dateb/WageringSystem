from typing import List

import numpy as np
from numpy import ndarray

from Model.Estimators.Estimator import Estimator
from Model.Estimators.util.metrics import get_accuracy
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class EnsembleAverageEstimator(Estimator):

    def __init__(self, feature_manager: FeatureManager, estimators: List[Estimator]):
        super().__init__(feature_manager)
        self.estimators = estimators

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        for estimator in self.estimators:
            estimator.fit_validate(train_sample, validation_sample)

        return 0.0

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        estimator_scores = []
        for estimator in self.estimators:
            scores = estimator.predict(train_sample, validation_sample, test_sample)
            estimator_scores.append(scores)

        average_scores = np.mean(estimator_scores, axis=0)

        test_sample.race_cards_dataframe['score'] = average_scores

        print(f"Test accuracy ensemble-average: {get_accuracy(test_sample)}")

        return average_scores

    def score_test_sample(self, test_sample: RaceCardsSample) -> None:
        estimator_scores = []
        for estimator in self.estimators:
            estimator.score_test_sample(test_sample)
            estimator_scores.append(test_sample.race_cards_dataframe['score'])

        average_scores = np.mean(estimator_scores, axis=0)

        test_sample.race_cards_dataframe['score'] = average_scores
