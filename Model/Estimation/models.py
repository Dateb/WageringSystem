import pickle
from abc import ABC

import numpy as np
import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimation.tuning import GBTTuner

from typing import Tuple, List
import lightgbm
from lightgbm import Booster, Dataset

from DataAbstraction.Present.Horse import Horse
from Model.Estimation.estimated_probabilities_creation import EstimationResult, RawWinProbabilizer, \
    Probabilizer
from Model.Estimation.util.dataset import HorseRacingSampleCreator, HorseRacingDataset
from Model.Estimation.util.metrics import get_accuracy
from ModelTuning import simulate_conf
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class Estimator(ABC):

    def __init__(
            self,
            feature_manager: FeatureManager,
            objective: str,
            objective_key: str,
            probabilizer: Probabilizer,
            label_name: str
    ):
        self.feature_manager = feature_manager
        self.objective_key = objective_key
        self.probabilizer = probabilizer
        self.label_name = label_name

        self.categorical_feature_names = []

        self.num_rounds = 500
        self.booster: Booster = None

        self.params = {
            "objective": objective,
            "metric": objective,

            "boosting_type": "gbdt",
            "deterministic": True,
            "force_row_wise": True,
            "device": "cpu",
            "verbose": -1,
            "feature_pre_filter": False,
            "n_jobs": -1,
        }

        random_seed = 30
        random_seed_parameters = [
            "seed", "data_random_seed", "feature_fraction_seed", "objective_seed",
            "bagging_seed", "extra_seed", "drop_seed"
        ]
        for parameter in random_seed_parameters:
            self.params[parameter] = random_seed

        self.tuner = GBTTuner(
            self.params, self.num_rounds, self.feature_manager.feature_names, n_hyperparameter_rounds=20
        )

    def fit(self, train_sample: RaceCardsSample) -> float:
        dataset = self.create_dataset(train_sample)

        if simulate_conf.RUN_MODEL_TUNER:
            gbt_config = self.tuner.run(dataset)
            with open(simulate_conf.GBT_CONFIG_PATH, "wb") as gbt_config_file:
                pickle.dump(gbt_config, gbt_config_file)

        with open(simulate_conf.GBT_CONFIG_PATH, "rb") as gbt_config_file:
            gbt_config = pickle.load(gbt_config_file)

        self.num_rounds = gbt_config.search_params["num_rounds"]
        del gbt_config.search_params["num_rounds"]
        self.params = {**self.params, **gbt_config.search_params}

        train_result = {}
        self.booster = lightgbm.train(
            num_boost_round=self.num_rounds,
            params=self.params,
            train_set=dataset.lightgbm_dataset,
            categorical_feature=self.categorical_feature_names,
            valid_sets=[dataset.lightgbm_dataset],
            valid_names=['train'],
            callbacks=[lightgbm.record_evaluation(train_result)],
        )

        self.booster.free_dataset()

        print(f"Train-{self.objective_key}: {train_result['train'][self.objective_key][-1]}")
        self.predict_probabilities(train_sample)

        eval_results = lightgbm.cv(
            params=self.params,
            train_set=dataset.lightgbm_dataset,
            categorical_feature=dataset.categorical_feature_names,
            return_cvbooster=False,
            stratified=False
        )

        cv_score = eval_results[f"valid {self.objective_key}-mean"][-1]

        print(f"Validation score: {cv_score}")

        self.show_feature_importance_scores()

        return 0.0

    def predict(self, sample: RaceCardsSample) -> Tuple[EstimationResult, float]:
        sample.race_cards_dataframe["prob"] = self.predict_probabilities(sample)

        estimation_result = self.probabilizer.create_estimation_result(
            sample,
            sample.race_cards_dataframe["prob"]
        )

        return estimation_result, 0

    def predict_probabilities(self, sample: RaceCardsSample) -> np.ndarray:
        dataset = self.create_dataset(sample)
        prob = self.booster.predict(dataset.lightgbm_dataset.data)
        print(f"Test accuracy of estimator {self.__class__.__name__}: {get_accuracy(sample, prob)}")

        return prob

    def create_dataset(self, sample: RaceCardsSample) -> HorseRacingDataset:
        pass

    def show_feature_importance_scores(self) -> None:
        importance_scores = self.booster.feature_importance(importance_type="gain")
        feature_importances = {self.feature_manager.feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}


        importance_sum = sum([importance for importance in list(sorted_feature_importances.values())])
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}

        avg_relative_importances = [relative_importance for feature_name, relative_importance in relative_feature_importances.items()
                                    if "AverageValueSource" in feature_name]

        print(f"Average values relative importances: {sum(avg_relative_importances)}")

        print(f"{importance_sum}: {relative_feature_importances}")


class AvgEstimator(Estimator):

    def __init__(self, feature_manager: FeatureManager, weak_estimators: List[Estimator]):
        super().__init__(
            feature_manager,
            objective="lambdarank",
            objective_key="ndcg@1",
            probabilizer=RawWinProbabilizer(),
            label_name=Horse.RANKING_LABEL_KEY
        )
        self.weak_estimators = weak_estimators

    def fit(self, train_sample: RaceCardsSample) -> float:
        for estimator in self.weak_estimators:
            estimator.fit(train_sample)

        return 0.0

    def predict_probabilities(self, sample: RaceCardsSample) -> np.ndarray:
        stacked_prob = np.zeros(shape=(len(sample.race_cards_dataframe)))

        for estimator in self.weak_estimators:
            estimator_prob = estimator.predict_probabilities(sample)
            stacked_prob += estimator_prob

        stacked_prob /= len(self.weak_estimators)

        print(f"Test accuracy of estimator {self.__class__.__name__}: {get_accuracy(sample, stacked_prob)}")

        return stacked_prob


class MaxEstimator(Estimator):

    def __init__(self, feature_manager: FeatureManager, weak_estimators: List[Estimator]):
        super().__init__(
            feature_manager,
            objective="lambdarank",
            objective_key="ndcg@1",
            probabilizer=RawWinProbabilizer(),
            label_name=Horse.RANKING_LABEL_KEY
        )
        self.weak_estimators = weak_estimators

    def fit(self, train_sample: RaceCardsSample) -> float:
        for estimator in self.weak_estimators:
            estimator.fit(train_sample)

        return 0.0

    def predict_probabilities(self, sample: RaceCardsSample) -> np.ndarray:
        stacked_prob = np.zeros(shape=(len(sample.race_cards_dataframe)))

        for estimator in self.weak_estimators:
            estimator_prob = estimator.predict_probabilities(sample)
            stacked_prob = np.maximum(stacked_prob, estimator_prob)

        print(f"Test accuracy of estimator {self.__class__.__name__}: {get_accuracy(sample, stacked_prob)}")

        return stacked_prob


class WinRankingEstimator(Estimator):

    def __init__(self, feature_manager: FeatureManager):
        super().__init__(
            feature_manager,
            objective="lambdarank",
            objective_key="ndcg@1",
            probabilizer=RawWinProbabilizer(),
            label_name=Horse.RANKING_LABEL_KEY
        )

        self.categorical_feature_names = self.feature_manager.categorical_feature_names

    def create_dataset(self, sample: RaceCardsSample) -> HorseRacingDataset:
        train_val_df = sample.race_cards_dataframe

        input_data = train_val_df[self.feature_manager.feature_names]
        label = train_val_df[self.label_name].astype(dtype="int")
        group = train_val_df.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        lightgbm_dataset = Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=self.categorical_feature_names,
        )

        return HorseRacingDataset(
            lightgbm_dataset=lightgbm_dataset,
            categorical_feature_names=self.categorical_feature_names
        )

    def predict_probabilities(self, sample: RaceCardsSample) -> np.ndarray:
        dataset = self.create_dataset(sample)
        scores = self.booster.predict(dataset.lightgbm_dataset.data)

        sample.race_cards_dataframe = self.set_win_probabilities(sample.race_cards_dataframe, scores)
        prob = sample.race_cards_dataframe["prob"]
        print(f"Test accuracy of estimator {self.__class__.__name__}: {get_accuracy(sample, prob)}")

        return prob

    def set_win_probabilities(self, race_cards_dataframe: pd.DataFrame, scores: np.ndarray) -> pd.DataFrame:
        race_cards_dataframe.loc[:, "score"] = scores

        race_cards_dataframe.loc[:, "exp_score"] = np.exp(race_cards_dataframe.loc[:, "score"])
        score_sums = race_cards_dataframe.groupby([RaceCard.RACE_ID_KEY]).agg(sum_exp_scores=("exp_score", "sum"))
        race_cards_dataframe = race_cards_dataframe.merge(right=score_sums, on=RaceCard.RACE_ID_KEY, how="left")

        race_cards_dataframe.loc[:, "prob"] = \
            (race_cards_dataframe.loc[:, "exp_score"] / race_cards_dataframe.loc[:, "sum_exp_scores"])

        race_cards_dataframe = race_cards_dataframe.drop("sum_exp_scores", axis=1)

        return race_cards_dataframe


class PaddedDataEstimator(Estimator):

    def create_dataset(self, sample: RaceCardsSample) -> HorseRacingDataset:
        train_val_df = sample.race_cards_dataframe

        features = train_val_df[self.feature_manager.feature_names]

        category_columns = features.select_dtypes(include='category').columns
        category_indices = [features.columns.get_loc(col) for col in category_columns]

        label_arr = train_val_df[self.label_name].to_numpy()
        horses_per_race_counts = train_val_df.groupby(RaceCard.RACE_ID_KEY).agg(count=(RaceCard.RACE_ID_KEY, 'count'))['count'].to_numpy()

        dataset = HorseRacingSampleCreator(features.to_numpy(), label_arr, horses_per_race_counts, category_indices)

        samples_X = []
        samples_y = []
        for race_idx in range(dataset.n_races):
            for horse_idx in range(dataset.get_n_horses_of_race(race_idx)):
                sample_features, sample_label = dataset.create_classification_sample(race_idx, horse_idx)
                samples_X.append(sample_features)
                samples_y.append(sample_label)

        X_df = pd.DataFrame(samples_X)
        y_df = pd.DataFrame(samples_y)

        if not self.categorical_feature_names:
            self.categorical_feature_names = list(X_df.select_dtypes(['object']).columns)

        for feature_name in self.categorical_feature_names:
            X_df[feature_name] = X_df[feature_name].astype('category')

        return HorseRacingDataset(
            lightgbm_dataset=Dataset(data=X_df, label=y_df),
            categorical_feature_names=self.categorical_feature_names
        )


class WinRegressionEstimator(PaddedDataEstimator):
    def __init__(self, feature_manager: FeatureManager):
        super().__init__(
            feature_manager,
            objective="gamma",
            objective_key="gamma",
            probabilizer=RawWinProbabilizer(),
            label_name=Horse.WIN_PROB_LABEL_KEY
        )


class WinClassificationEstimator(PaddedDataEstimator):

    def __init__(self, feature_manager: FeatureManager):
        super().__init__(
            feature_manager,
            objective="binary",
            objective_key="binary_logloss",
            probabilizer=RawWinProbabilizer(),
            label_name=Horse.HAS_WON_LABEL_KEY
        )

