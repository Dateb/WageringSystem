from typing import List

import lightgbm
import pandas as pd

from lightgbm import Dataset
from numpy import ndarray
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimation.Estimator import Estimator
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesRanker(Estimator):

    ranking_seed = 30

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "metric": "lambdarank",
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
        self.feature_names = [feature.get_name() for feature in features]

        self.categorical_feature_names = [feature.get_name() for feature in features if feature.is_categorical]

        self.set_parameter_set(search_params)
        self.booster = None

    def fit(self, samples_train: pd.DataFrame, num_boost_round: int):
        self.booster = lightgbm.train(
            self.parameter_set,
            train_set=self.get_dataset(samples_train),
            categorical_feature=self.categorical_feature_names,
            num_boost_round=num_boost_round,
        )

    def cross_validate(self, samples_train: pd.DataFrame, num_boost_round: int) -> dict:
        cv_result = lightgbm.cv(
            self.parameter_set,
            train_set=self.get_dataset(samples_train),
            categorical_feature=self.categorical_feature_names,
            shuffle=False,
            num_boost_round=num_boost_round,
            nfold=5,
        )

        return cv_result

    def get_dataset(self, samples_train: pd.DataFrame) -> Dataset:
        input_data = samples_train[self.feature_names]
        label = samples_train[self.label_name].astype(dtype="int")
        group = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        return Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=self.categorical_feature_names,
        )

    def score_test_races(self, race_cards_sample: RaceCardsSample) -> ndarray:
        race_cards_dataframe = race_cards_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        scores = self.booster.predict(X)

        return scores
