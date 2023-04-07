import random
from typing import List

import lightgbm
import numpy as np
import pandas as pd

from lightgbm import Dataset
from numpy import ndarray
from sklearn.metrics import accuracy_score

from DataAbstraction.Present.Horse import Horse
from Model.Estimation.Estimator import Estimator
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
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
        super().__init__(features, Horse.RELEVANCE_KEY)
        if not search_params:
            search_params = {}

        self.features = features
        self.feature_names = [feature.get_name() for feature in features]

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

        y_pred = self.booster.predict(X)
        y_pred = [1 if p >= 0.5 else 0 for p in y_pred]

        train_acc = accuracy_score(y, y_pred)
        print(f"train: {train_acc}")

    def get_X_and_y(self, sample: pd.DataFrame):
        sample["shift"] = (np.random.rand(len(sample)) - 0.5) * 4
        sample["shifted_odds"] = sample[Horse.CURRENT_PLACE_ODDS_KEY] + sample["shift"]
        sample["shifted_odds"] = sample["shifted_odds"].astype(float)

        sample["label"] = sample["shift"] >= 0

        X = sample[self.feature_names + ["shifted_odds"]]
        y = sample["label"].astype(dtype="int")

        return X, y

    def score_races(self, race_cards_sample: RaceCardsSample) -> ndarray:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X, y = self.get_X_and_y(race_cards_dataframe)
        scores = self.booster.predict(X)

        y_pred = self.booster.predict(X)
        y_pred = [1 if p >= 0.5 else 0 for p in y_pred]

        test_acc = accuracy_score(y, y_pred)
        print(f"test: {test_acc}")

        return scores
