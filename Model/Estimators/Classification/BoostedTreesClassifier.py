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
from Model.Estimators.estimated_probabilities_creation import EstimationResult, WinProbabilizer, RawWinProbabilizer
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
        num_rounds = trial.suggest_int("num_rounds", 500, 800)

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


class BoostedTreesClassifier(Estimator):
    RANKING_SEED = 30

    FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "multiclass",
        "metric": "multi_logloss",
        "num_class": 2,
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
        self.probabilizer = RawWinProbabilizer()
        self.label_name = Horse.HAS_PLACED_LABEL_KEY
        self.feature_manager = feature_manager
        self.booster: Booster = None

        self.categorical_feature_names = [feature.get_name() for feature in feature_manager.features if feature.is_categorical]
        self.cat_gbt_feature_names = [f"{cat_feature_name}_gbt" for cat_feature_name in self.categorical_feature_names]
        self.feature_names = self.feature_manager.numerical_feature_names + self.cat_gbt_feature_names

        # self.parameter_set = {**self.FIXED_PARAMS}

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        self.fit_validate(train_sample, validation_sample)

        print("Model tuning completed!")
        test_loss = self.score_test_sample(test_sample)

        # test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        print(f"Test accuracy gbt-model: {get_accuracy(test_sample)}")

        estimation_result = self.probabilizer.create_estimation_result(test_sample, test_sample.race_cards_dataframe["score"])

        return estimation_result, test_loss

    def score_test_sample(self, test_sample: RaceCardsSample):
        #TODO: The categorical creation/deletion is also used in the predict function. Refactor the duplication.
        for cat_feature_name in self.categorical_feature_names:
            cat_gbt_feature_name = f"{cat_feature_name}_gbt"
            test_sample.race_cards_dataframe[cat_gbt_feature_name] = test_sample.race_cards_dataframe[cat_feature_name].astype('category')

        race_cards_dataframe = test_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        class_probs = self.booster.predict(X)

        test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        test_sample.race_cards_dataframe["score"] = class_probs[:, 1]

        return 0

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        train_val_df = pd.concat(
            objs=[train_sample.race_cards_dataframe, validation_sample.race_cards_dataframe],
            ignore_index=True,
            axis=0
        )

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
        # study.optimize(cv_objective, n_trials=100)
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

        self.num_boost_round = 554
        search_params = {'num_leaves': 5, 'lambda_l1': 9.56619418630856e-05, 'lambda_l2': 0.00022053693841990408,
         'feature_fraction': 0.41424974477594756, 'bagging_fraction': 0.8352734213423343, 'bagging_freq': 5,
         'min_child_samples': 133}

        self.params = {**self.FIXED_PARAMS, **search_params}

        # self.booster = self.rfe_booster(train_val_df)

        self.booster, sorted_feature_importances = self.get_sorted_feature_importances(dataset, self.feature_names, self.cat_gbt_feature_names)
        importance_sum = self.get_importance_sum(sorted_feature_importances)
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}

        print(f"{importance_sum}: {relative_feature_importances}")

        return 0.0

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

        return Dataset(
            data=input_data,
            label=label,
            categorical_feature=categorical_feature_names
        )
