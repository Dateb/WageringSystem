from copy import deepcopy
from typing import List, Tuple

import numpy as np

from Model.Estimators.Estimator import Estimator
from Model.Estimators.estimated_probabilities_creation import EstimationResult, AggWinProbabilizer
from Model.Estimators.util.metrics import get_accuracy, get_accuracy_by_win_probability
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class EnsembleAverageEstimator(Estimator):

    def __init__(self, feature_manager: FeatureManager, estimators: List[Estimator]):
        super().__init__(feature_manager)
        self.estimators = estimators
        self.probabilizer = AggWinProbabilizer()

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        estimator_scores = []
        for estimator in self.estimators:
            scores, test_loss = estimator.predict(train_sample, validation_sample, test_sample)
            estimator_scores.append(scores)

        estimation_result = self.probabilizer.create_estimation_result(test_sample, estimator_scores)

        return estimation_result, 0.0

    def score_test_sample(self, test_sample: RaceCardsSample) -> None:
        estimator_scores = []
        for estimator in self.estimators:
            estimator.score_test_sample(test_sample)
            estimator_scores.append(test_sample.race_cards_dataframe['score'])

        average_scores = np.mean(estimator_scores, axis=0)

        test_sample.race_cards_dataframe['score'] = average_scores
