from typing import List

import lightgbm
import pandas as pd

from lightgbm import Dataset
from numpy import ndarray
from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesRanker:

    ranking_seed = 30

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "xendcg",
        "metric": "xendcg",
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

    def __init__(self, features: List[FeatureExtractor], search_params: dict, num_boost_rounds: int):
        self.features = features
        self.feature_names = [feature.get_name() for feature in features]
        self.categorical_feature_names = [feature.get_name() for feature in features if feature.is_categorical]

        self.num_boost_rounds = num_boost_rounds
        self.search_params = search_params
        self.parameter_set = {**self._FIXED_PARAMS, **search_params}
        self.label_name = Horse.RELEVANCE_KEY
        self.booster = None

    def fit(self, sample: pd.DataFrame):
        self.booster = lightgbm.train(
            self.parameter_set,
            train_set=self.get_dataset(sample),
            categorical_feature=self.categorical_feature_names,
            num_boost_round=self.num_boost_rounds,
        )

        # importance_scores = self.booster.feature_importance(importance_type="gain")
        # feature_importances = {self.feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        # sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}
        # importance_sum = sum([importance for importance in list(feature_importances.values())])
        # print(f"{importance_sum}: {sorted_feature_importances}")

    def predict(self, sample: pd.DataFrame) -> ndarray:
        scores = self.booster.predict(sample[self.feature_names])

        return scores

    def cross_validate(self, train_sample: pd.DataFrame) -> dict:
        cv_result = lightgbm.cv(
            self.parameter_set,
            metrics="MAP",
            train_set=self.get_dataset(train_sample),
            categorical_feature=self.categorical_feature_names,
            shuffle=False,
            num_boost_round=self.num_boost_rounds,
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
