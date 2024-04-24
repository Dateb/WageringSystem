from copy import copy
from dataclasses import dataclass
from typing import List

import lightgbm
import numpy as np
from lightgbm import Dataset

import optuna

from Model.Estimation.dataset_factory import DatasetFactory


@dataclass
class GBTConfig:

    search_params: dict
    feature_names: List[str]


class GBTTuner:
    def __init__(
            self,
            fixed_params: dict,
            num_boost_rounds: int,
            feature_names: List[str],
            categorical_feature_names: List[str],
            n_hyperparameter_rounds: int = 20,
    ):
        self.fixed_params = fixed_params
        self.num_boost_rounds = num_boost_rounds
        self.feature_names = feature_names
        self.categorical_feature_names = categorical_feature_names
        self.n_hyperparameter_rounds = n_hyperparameter_rounds

        self.best_score = -np.inf
        self.best_search_params = {}
        self.removed_feature_names = []
        self.is_feature_selection_completed = False

    def run(self, dataset_factory: DatasetFactory) -> GBTConfig:
        gbt_config = GBTConfig(search_params={}, feature_names=self.feature_names)
        while not self.is_feature_selection_completed:
            dataset = dataset_factory.create_dataset(self.feature_names, self.categorical_feature_names)
            gbt_config.search_params = self.get_hyperparameters(dataset)

            print(f"Executing feature selection...")
            self.feature_names = self.get_feature_names(dataset_factory, gbt_config)
            self.categorical_feature_names = [feature_name for feature_name in self.feature_names if feature_name in self.categorical_feature_names]

        gbt_config.feature_names = self.feature_names
        return gbt_config

    def get_hyperparameters(self, dataset: Dataset) -> dict:
        cv_objective = GBTObjective(
            fixed_params=self.fixed_params,
            num_rounds=self.num_boost_rounds,
            dataset=dataset,
            cat_feature_names=self.categorical_feature_names
        )

        study = optuna.create_study(direction="maximize")

        study.optimize(cv_objective, n_trials=self.n_hyperparameter_rounds)

        print("Number of finished trials: {}".format(len(study.trials)))

        print("Best trial:")
        trial = study.best_trial

        print("  Value: {}".format(trial.value))

        print("  Params: ")
        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))

        if study.best_trial.value > self.best_score:
            self.best_score = study.best_trial.value
            self.best_search_params = trial.params
            print(f"Using new search params with score: {self.best_score}")
            return study.best_trial.params
        else:
            return self.best_search_params

    def get_feature_names(self, dataset_factory: DatasetFactory, gbt_config: GBTConfig) -> List[str]:
        dataset = dataset_factory.create_dataset(self.feature_names, self.categorical_feature_names)

        sorted_feature_importances = self.get_sorted_feature_importances(dataset, gbt_config, self.feature_names, self.categorical_feature_names)
        importance_sum = self.get_importance_sum(sorted_feature_importances)
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}
        ordered_feature_names = list(relative_feature_importances.keys())

        best_cv_score = self.best_score

        best_feature_names_subset = copy(self.feature_names)
        for feature_name in ordered_feature_names:
            feature_names_subset = copy(best_feature_names_subset)
            feature_names_subset.remove(feature_name)

            categorical_feature_names_subset = [feature_name for feature_name in feature_names_subset if feature_name in self.categorical_feature_names]

            dataset = dataset_factory.create_dataset(feature_names_subset, categorical_feature_names_subset)

            eval_results = lightgbm.cv(
                params={**self.fixed_params, **gbt_config.search_params},
                train_set=dataset,
                num_boost_round=self.num_boost_rounds,
                categorical_feature=categorical_feature_names_subset,
                return_cvbooster=True
            )

            cv_score = eval_results["valid ndcg@5-mean"][-1]

            if cv_score > best_cv_score:
                self.best_score = best_cv_score
                self.removed_feature_names.append(feature_name)
                best_cv_score = cv_score

                sorted_feature_importances = self.get_sorted_feature_importances(dataset, gbt_config,
                                                                                 feature_names_subset,
                                                                                 categorical_feature_names_subset)
                importance_sum = self.get_importance_sum(sorted_feature_importances)

                relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                                sorted_feature_importances.items()}

                print(f"{importance_sum}: {relative_feature_importances}")
                print(f"Best score: {best_cv_score}")
                print(f"Removed features: {self.removed_feature_names}")

                best_feature_names_subset.remove(feature_name)

                return best_feature_names_subset

        self.is_feature_selection_completed = True
        return best_feature_names_subset

    def get_sorted_feature_importances(self, dataset: Dataset, gbt_config: GBTConfig, feature_names: List[str], categorical_feature_names: List[str]) -> dict:
        booster = lightgbm.train(
            num_boost_round=self.num_boost_rounds,
            params={**self.fixed_params, **gbt_config.search_params},
            train_set=dataset,
            categorical_feature=categorical_feature_names,
        )

        importance_scores = booster.feature_importance(importance_type="gain")
        feature_importances = {feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        sorted_feature_importances = {k: v for k, v in reversed(sorted(feature_importances.items(), key=lambda item: item[1]))}

        booster.free_dataset()

        return sorted_feature_importances

    def get_importance_sum(self, sorted_feature_importances: dict) -> float:
        importance_sum = sum([importance for importance in list(sorted_feature_importances.values())])

        return importance_sum


class GBTObjective:
    def __init__(self, fixed_params: dict, num_rounds: int, dataset: Dataset, cat_feature_names: List[str]):
        self.fixed_params = fixed_params
        self.num_rounds = num_rounds
        self.dataset = dataset
        self.cat_feature_names = cat_feature_names

    def __call__(self, trial):
        search_params = {
            "num_leaves": trial.suggest_int("num_leaves", 2, 8),
            "lambda_l1": trial.suggest_float("lambda_l1", 1e-8, 10.0, log=True),
            "lambda_l2": trial.suggest_float("lambda_l2", 1e-8, 10.0, log=True),
            "feature_fraction": trial.suggest_float("feature_fraction", 0.3, 1.0),
            "bagging_fraction": trial.suggest_float("bagging_fraction", 0.3, 1.0),
            "bagging_freq": trial.suggest_int("bagging_freq", 1, 7),
            "min_child_samples": trial.suggest_int("min_child_samples", 80, 140),
        }

        params = {**self.fixed_params, **search_params}

        eval_results = lightgbm.cv(
            params=params,
            train_set=self.dataset,
            num_boost_round=self.num_rounds,
            categorical_feature=self.cat_feature_names,
            return_cvbooster=True
        )

        cv_score = eval_results["valid ndcg@5-mean"][-1]

        return cv_score
