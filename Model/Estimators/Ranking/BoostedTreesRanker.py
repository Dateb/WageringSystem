from copy import copy
from typing import Tuple, List

import optuna
import lightgbm
import pandas as pd
from lightgbm import Dataset, Booster, CVBooster
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.Estimator import Estimator
from Model.Estimators.estimated_probabilities_creation import EstimationResult, WinProbabilizer
from Model.Estimators.util.metrics import get_accuracy
from ModelTuning import simulate_conf
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


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

        cv_score = eval_results["valid ndcg@1-mean"][-1]

        return cv_score


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

        self.categorical_feature_names = [feature.get_name() for feature in feature_manager.features if feature.is_categorical]
        self.cat_gbt_feature_names = [f"{cat_feature_name}_gbt" for cat_feature_name in self.categorical_feature_names]
        self.feature_names = self.feature_manager.numerical_feature_names + self.cat_gbt_feature_names

        # self.parameter_set = {**self.FIXED_PARAMS}

    def predict(self, sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        test_loss = self.score_test_sample(sample)

        # test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        print(f"Test accuracy gbt-model: {get_accuracy(sample)}")

        estimation_result = self.probabilizer.create_estimation_result(sample, sample.race_cards_dataframe["score"])

        return estimation_result, test_loss

    def score_test_sample(self, test_sample: RaceCardsSample):
        #TODO: The categorical creation/deletion is also used in the predict function. Refactor the duplication.
        for cat_feature_name in self.categorical_feature_names:
            cat_gbt_feature_name = f"{cat_feature_name}_gbt"
            test_sample.race_cards_dataframe[cat_gbt_feature_name] = test_sample.race_cards_dataframe[cat_feature_name].astype('category')

        race_cards_dataframe = test_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        scores = self.booster.predict(X)

        test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        test_sample.race_cards_dataframe["score"] = scores

        return 0

    def fit(self, train_sample: RaceCardsSample) -> float:
        train_val_df = train_sample.race_cards_dataframe

        for cat_feature_name in self.categorical_feature_names:
            cat_gbt_feature_name = f"{cat_feature_name}_gbt"
            train_val_df[cat_gbt_feature_name] = train_val_df[cat_feature_name].astype('category')

        dataset = self.get_dataset(train_val_df, self.feature_names, self.cat_gbt_feature_names)

        # cv_objective = GBTObjective(
        #     fixed_params=self.FIXED_PARAMS,
        #     dataset=dataset,
        #     cat_feature_names=self.cat_gbt_feature_names
        # )
        #
        # study = optuna.create_study(direction="maximize")
        #
        # study.optimize(cv_objective, n_trials=30)
        #
        # print("Number of finished trials: {}".format(len(study.trials)))
        #
        # print("Best trial:")
        # trial = study.best_trial
        #
        # print("  Value: {}".format(trial.value))
        #
        # print("  Params: ")
        # for key, value in trial.params.items():
        #     print("    {}: {}".format(key, value))
        #
        # search_params = trial.params
        #
        # self.num_boost_round = trial.params["num_rounds"]
        # del trial.params["num_rounds"]

        self.num_boost_round = 857
        search_params = {'num_leaves': 4, 'lambda_l1': 3.2672839941029697, 'lambda_l2': 1.3113698402790085e-05,
         'feature_fraction': 0.3824645993260089, 'bagging_fraction': 0.7621282724793796, 'bagging_freq': 4,
         'min_child_samples': 91}

        self.params = {**self.FIXED_PARAMS, **search_params}

        # self.booster = self.rfe_booster(train_val_df)

        self.booster, sorted_feature_importances = self.get_sorted_feature_importances(dataset, self.feature_names, self.cat_gbt_feature_names)
        importance_sum = self.get_importance_sum(sorted_feature_importances)
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}

        print(f"{importance_sum}: {relative_feature_importances}")

        return 0.0

    def rfe_booster(self, df: pd.DataFrame):
        dataset = self.get_dataset(df, self.feature_names, self.cat_gbt_feature_names)

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

    def get_dataset(self, samples_train: pd.DataFrame, feature_names: List[str], categorical_feature_names: List[str]) -> Dataset:
        input_data = samples_train[feature_names]
        label = samples_train[self.label_name].astype(dtype="int")
        group = samples_train.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        return Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=categorical_feature_names
        )
