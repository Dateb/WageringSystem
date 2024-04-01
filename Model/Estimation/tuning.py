import json
from typing import List

import lightgbm
from lightgbm import Dataset

import optuna

from ModelTuning import simulate_conf


class GBTTuner:
    def __init__(self, fixed_params: dict, categorical_feature_names: List[str], n_hyperparameter_rounds: int = 2):
        self.fixed_params = fixed_params
        self.categorical_feature_names = categorical_feature_names
        self.n_hyperparameter_rounds = n_hyperparameter_rounds

    def run_hyperparameter_tuning(self, dataset: Dataset) -> dict:
        cv_objective = GBTObjective(
            fixed_params=self.fixed_params,
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

        with open(simulate_conf.PARAMS_PATH, "w") as param_file:
            json.dump(trial.params, param_file)

        return trial.params


class GBTObjective:
    def __init__(self, fixed_params: dict, dataset: Dataset, cat_feature_names: List[str]):
        self.fixed_params = fixed_params
        self.dataset = dataset
        self.cat_feature_names = cat_feature_names

    def __call__(self, trial):
        num_rounds = trial.suggest_int("num_rounds", 700, 1100)

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
            num_boost_round=num_rounds,
            categorical_feature=self.cat_feature_names,
            return_cvbooster=True
        )

        cv_score = eval_results["valid ndcg@5-mean"][-1]

        return cv_score
