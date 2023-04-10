from typing import List

import lightgbm
import pandas as pd

from lightgbm import Dataset

from DataAbstraction.Present.Horse import Horse
from Model.Estimation.Estimator import Estimator, ClassificationResult
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class OddsShiftClassifier(Estimator):

    ranking_seed = 30

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "binary",
        "metric": "binary",
        "verbose": -1,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
        "device": "cpu",

        "seed": ranking_seed,
        "data_random_seed": ranking_seed,
        "feature_fraction_seed": ranking_seed,
        "objective_seed": ranking_seed,
        "bagging_seed": ranking_seed,
        "extra_seed": ranking_seed,
        "drop_seed": ranking_seed,
    }

    def __init__(self, features: List[FeatureExtractor], search_params: dict):
        super().__init__(features, Horse.LABEL)
        if not search_params:
            search_params = {}

        self.features = features

        self.categorical_feature_names = [feature.get_name() for feature in features if feature.is_categorical]

        self.set_parameter_set(search_params)
        self.booster = None

    def fit(self, samples_train: pd.DataFrame, num_boost_round: int):
        X, y = self.get_X_and_y(samples_train)

        train_set = Dataset(
            data=X,
            label=y,
            categorical_feature=self.categorical_feature_names,
        )

        self.booster = lightgbm.train(
            self.parameter_set,
            train_set=train_set,
            categorical_feature=self.categorical_feature_names,
            num_boost_round=num_boost_round,
        )

    def get_X_and_y(self, sample: pd.DataFrame):
        X = sample[FeatureManager.get_feature_names(self.features)]
        y = sample[self.label_name].astype(dtype="int")

        return X, y

    def score_test_races(self, race_cards_sample: RaceCardsSample) -> ClassificationResult:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X, y_true = self.get_X_and_y(race_cards_dataframe)

        y_pred = self.booster.predict(X)

        classification_result = ClassificationResult(
            y_true.to_numpy(),
            y_pred,
            race_cards_dataframe[Horse.ODDS_SHIFT].to_numpy()
        )

        return classification_result
