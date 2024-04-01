import json
import pickle
from abc import ABC, abstractmethod
from typing import Tuple

from Model.Estimation.estimated_probabilities_creation import EstimationResult
from Model.Estimation.tuning import GBTTuner
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample

from copy import copy
from typing import Tuple, List
import lightgbm
import pandas as pd
from lightgbm import Dataset, Booster, CVBooster
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimation.estimated_probabilities_creation import EstimationResult, WinProbabilizer
from Model.Estimation.util.metrics import get_accuracy
from ModelTuning import simulate_conf
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Estimator(ABC):

    def __init__(self, feature_manager: FeatureManager):
        self.feature_manager = feature_manager

    @abstractmethod
    def predict(self, sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        pass

    def fit(self, train_sample: RaceCardsSample) -> float:
        pass

    def score_test_sample(self, test_sample: RaceCardsSample):
        pass


class BoostedTreesRanker(Estimator):
    RANKING_SEED = 30

    FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "lambdarank",
        "deterministic": True,
        "force_row_wise": True,
        "device": "cpu",
        "verbose": -1,
        "feature_pre_filter": False,
        "n_jobs": -1,

        "seed": RANKING_SEED,
        "data_random_seed": RANKING_SEED,
        "feature_fraction_seed": RANKING_SEED,
        "objective_seed": RANKING_SEED,
        "bagging_seed": RANKING_SEED,
        "extra_seed": RANKING_SEED,
        "drop_seed": RANKING_SEED,
    }

    def __init__(self, feature_manager: FeatureManager):
        super().__init__(feature_manager)
        self.probabilizer = WinProbabilizer()
        self.label_name = Horse.RANKING_LABEL_KEY
        self.feature_manager = feature_manager
        self.booster: Booster = None

        self.categorical_feature_names = [feature.name for feature in feature_manager.features if feature.is_categorical]
        self.feature_names = self.feature_manager.numerical_feature_names + self.categorical_feature_names

        self.tuner = GBTTuner(self.FIXED_PARAMS, self.feature_names, self.categorical_feature_names)

    def predict(self, sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        test_loss = self.score_test_sample(sample)

        print(f"Test accuracy gbt-model: {get_accuracy(sample)}")

        estimation_result = self.probabilizer.create_estimation_result(sample, sample.race_cards_dataframe["score"])

        return estimation_result, test_loss

    def score_test_sample(self, test_sample: RaceCardsSample):
        race_cards_dataframe = test_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        scores = self.booster.predict(X)

        test_sample.race_cards_dataframe["score"] = scores

        return 0

    def fit(self, train_sample: RaceCardsSample) -> float:
        train_val_df = train_sample.race_cards_dataframe

        dataset = self.get_dataset(train_val_df, self.feature_names, self.categorical_feature_names)

        if simulate_conf.RUN_MODEL_TUNER:
            gbt_config = self.tuner.run(dataset)
            with open(simulate_conf.GBT_CONFIG_PATH, "wb") as gbt_config_file:
                pickle.dump(gbt_config, gbt_config_file)

        with open(simulate_conf.GBT_CONFIG_PATH, "rb") as gbt_config_file:
            gbt_config = pickle.load(gbt_config_file)

        self.num_boost_round = gbt_config.search_params["num_rounds"]
        del gbt_config.search_params["num_rounds"]

        self.params = {**self.FIXED_PARAMS, **gbt_config.search_params}

        # self.booster = self.rfe_booster(train_val_df)

        self.booster, sorted_feature_importances = self.get_sorted_feature_importances(dataset, self.feature_names, self.categorical_feature_names)
        importance_sum = self.get_importance_sum(sorted_feature_importances)
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}

        print(f"{importance_sum}: {relative_feature_importances}")

        return 0.0

    def rfe_booster(self, df: pd.DataFrame):
        dataset = self.get_dataset(df, self.feature_names, self.categorical_feature_names)

        sorted_feature_importances = self.get_sorted_feature_importances(dataset, self.feature_names, self.cat_gbt_feature_names)
        importance_sum = self.get_importance_sum(sorted_feature_importances)
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}
        ordered_feature_names = list(relative_feature_importances.keys())

        eval_results = lightgbm.cv(
            params=self.params,
            train_set=dataset,
            num_boost_round=self.num_boost_round,
            categorical_feature=self.cat_gbt_feature_names,
            return_cvbooster=True
        )

        best_cv_score = eval_results["valid ndcg@1-mean"][-1]

        removed_feature_names = []
        improvement_found = True
        while improvement_found:
            improvement_found = False
            for feature_name in ordered_feature_names:
                if not improvement_found:
                    feature_name_subset = copy(self.feature_names)
                    feature_name_subset.remove(feature_name)

                    categorical_feature_name_subset = copy(self.cat_gbt_feature_names)
                    if feature_name in self.cat_gbt_feature_names:
                        categorical_feature_name_subset.remove(feature_name)

                    dataset = self.get_dataset(df, feature_name_subset, categorical_feature_name_subset)

                    eval_results = lightgbm.cv(
                        params=self.params,
                        train_set=dataset,
                        num_boost_round=self.num_boost_round,
                        categorical_feature=categorical_feature_name_subset,
                        return_cvbooster=True
                    )

                    cv_score = eval_results["valid ndcg@1-mean"][-1]

                    sorted_feature_importances = self.get_sorted_feature_importances(dataset, feature_name_subset, categorical_feature_name_subset)
                    importance_sum = self.get_importance_sum(sorted_feature_importances)

                    relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                                    sorted_feature_importances.items()}

                    if cv_score > best_cv_score:
                        removed_feature_names.append(feature_name)
                        print(f"{importance_sum}: {relative_feature_importances}")
                        print(f"Best score: {best_cv_score}")
                        print(f"Removed features: {removed_feature_names}")
                        best_cv_score = cv_score
                        improvement_found = True

                        self.feature_names.remove(feature_name)
                        if feature_name in self.categorical_feature_names:
                            self.categorical_feature_names.remove(feature_name)

                        ordered_feature_names = list(relative_feature_importances.keys())

        dataset = self.get_dataset(df, self.feature_names, self.categorical_feature_names)
        booster = lightgbm.train(
            num_boost_round=self.num_boost_round,
            params=self.params,
            train_set=dataset,
            categorical_feature=self.cat_gbt_feature_names,
        )

        return booster

    def get_sorted_feature_importances(self, dataset: Dataset, feature_names: List[str], categorical_feature_names: List[str]):
        booster = lightgbm.train(
            num_boost_round=self.num_boost_round,
            params=self.params,
            train_set=dataset,
            categorical_feature=categorical_feature_names,
        )

        importance_scores = booster.feature_importance(importance_type="gain")
        feature_importances = {feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}

        booster.free_dataset()

        return booster, sorted_feature_importances

    def get_importance_sum(self, sorted_feature_importances: dict) -> float:
        importance_sum = sum([importance for importance in list(sorted_feature_importances.values())])

        return importance_sum

    def get_dataset(self, sample: pd.DataFrame, feature_names: List[str], categorical_feature_names: List[str]) -> Dataset:
        input_data = sample[feature_names]
        label = sample[self.label_name].astype(dtype="int")
        group = sample.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        return Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=categorical_feature_names
        )
