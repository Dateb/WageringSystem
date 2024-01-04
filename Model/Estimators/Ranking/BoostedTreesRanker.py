from typing import Tuple, List

import optuna
import lightgbm
import pandas as pd
from lightgbm import Dataset, Booster, CVBooster
from numpy import ndarray

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.Estimator import Estimator
from Model.Estimators.util.metrics import get_accuracy
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class GBTObjective:
    def __init__(self, fixed_params: dict, dataset: Dataset, cat_feature_names: List[str]):
        self.fixed_params = fixed_params
        self.dataset = dataset
        self.cat_feature_names = cat_feature_names

    def __call__(self, trial):
        num_rounds = trial.suggest_int("num_rounds", 150, 300)

        search_params = {
            "num_leaves": trial.suggest_int("num_leaves", 10, 20),
            "lambda_l1": trial.suggest_float("lambda_l1", 1e-8, 10.0, log=True),
            "lambda_l2": trial.suggest_float("lambda_l2", 1e-8, 10.0, log=True),
            "feature_fraction": trial.suggest_float("feature_fraction", 0.4, 1.0),
            "bagging_fraction": trial.suggest_float("bagging_fraction", 0.4, 1.0),
            "bagging_freq": trial.suggest_int("bagging_freq", 1, 7),
            "min_child_samples": trial.suggest_int("min_child_samples", 60, 120),
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
        "n_jobs": -1,
        "device": "cpu",
        "verbose": -1,
        "feature_pre_filter": False,

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
        self.label_name = Horse.CLASSIFICATION_LABEL_KEY
        self.feature_manager = feature_manager
        self.booster: Booster = None

        self.categorical_feature_names = [feature.get_name() for feature in feature_manager.features if feature.is_categorical]
        self.cat_gbt_feature_names = [f"{cat_feature_name}_gbt" for cat_feature_name in self.categorical_feature_names]
        self.feature_names = self.feature_manager.numerical_feature_names + self.cat_gbt_feature_names

        # self.parameter_set = {**self.FIXED_PARAMS}

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> Tuple[ndarray, float]:
        self.fit_validate(train_sample, validation_sample)

        print("Model tuning completed!")
        test_loss = self.score_test_sample(test_sample)

        # test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        print(f"Test accuracy gbt-model: {get_accuracy(test_sample)}")

        return test_sample.race_cards_dataframe["score"], test_loss

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

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        train_val_df = pd.concat(
            objs=[train_sample.race_cards_dataframe, validation_sample.race_cards_dataframe],
            ignore_index=True,
            axis=0
        )

        for cat_feature_name in self.categorical_feature_names:
            cat_gbt_feature_name = f"{cat_feature_name}_gbt"
            train_val_df[cat_gbt_feature_name] = train_val_df[cat_feature_name].astype('category')

        dataset = self.get_dataset(train_val_df)

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

        # search_params = trial.params

        search_params = {
            "num_rounds": 266,
            "num_leaves": 14,
            "lambda_l1": 7.345368276137748,
            "lambda_l2": 1.4236994442124007,
            "feature_fraction": 0.45775599282359614,
            "bagging_fraction": 0.8937420818276652,
            "bagging_freq": 7,
            "min_child_samples": 86
        }

        params = {**self.FIXED_PARAMS, **search_params}
        self.booster = lightgbm.train(
            params=params,
            train_set=dataset,
            categorical_feature=self.cat_gbt_feature_names,
        )

        importance_scores = self.booster.feature_importance(importance_type="gain")
        feature_importances = {self.feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}
        importance_sum = sum([importance for importance in list(feature_importances.values())])
        print(f"{importance_sum}: {sorted_feature_importances}")

        self.booster.free_dataset()

        return 0.0

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
