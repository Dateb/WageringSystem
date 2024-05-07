import pickle
from abc import ABC, abstractmethod

from Model.Estimation.dataset_factory import DatasetFactory
from Model.Estimation.tuning import GBTTuner

from typing import Tuple
import lightgbm
from lightgbm import Booster

from DataAbstraction.Present.Horse import Horse
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
        self.num_rounds = 2000
        self.probabilizer = WinProbabilizer()
        self.label_name = Horse.RANKING_LABEL_KEY
        self.feature_manager = feature_manager
        self.booster: Booster = None

        self.categorical_feature_names = [feature.name for feature in feature_manager.features if feature.is_categorical]
        self.feature_names = self.feature_manager.numerical_feature_names + self.categorical_feature_names

        self.tuner = GBTTuner(self.FIXED_PARAMS, self.num_rounds, self.feature_names, self.categorical_feature_names)

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

        dataset_factory = DatasetFactory(train_val_df, self.label_name)

        if simulate_conf.RUN_MODEL_TUNER:
            gbt_config = self.tuner.run(dataset_factory)
            with open(simulate_conf.GBT_CONFIG_PATH, "wb") as gbt_config_file:
                pickle.dump(gbt_config, gbt_config_file)

        with open(simulate_conf.GBT_CONFIG_PATH, "rb") as gbt_config_file:
            gbt_config = pickle.load(gbt_config_file)

        missing_feature_names = [feature_name for feature_name in self.feature_names if feature_name not in gbt_config.feature_names]

        if missing_feature_names:
            print(f"WARNING: Features that are computed, but not included in the model: {missing_feature_names}")

        # self.feature_names = gbt_config.feature_names
        self.params = {**self.FIXED_PARAMS, **gbt_config.search_params}

        self.categorical_feature_names = [feature_name for feature_name in gbt_config.feature_names
                                          if feature_name in self.categorical_feature_names]
        dataset = dataset_factory.create_dataset(self.feature_names, self.categorical_feature_names)

        self.booster = lightgbm.train(
            num_boost_round=self.num_rounds,
            params=self.params,
            train_set=dataset,
            categorical_feature=self.categorical_feature_names,
        )

        importance_scores = self.booster.feature_importance(importance_type="gain")
        feature_importances = {self.feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}

        self.booster.free_dataset()

        importance_sum = sum([importance for importance in list(sorted_feature_importances.values())])
        relative_feature_importances = {k: round((v / importance_sum) * 100, 2) for k, v in
                                        sorted_feature_importances.items()}

        avg_relative_importances = [relative_importance for feature_name, relative_importance in relative_feature_importances.items()
                                    if "AverageValueSource" in feature_name]

        print(f"Average values relative importances: {sum(avg_relative_importances)}")

        print(f"{importance_sum}: {relative_feature_importances}")

        eval_results = lightgbm.cv(
            params=self.params,
            train_set=dataset,
            num_boost_round=self.num_rounds,
            categorical_feature=self.categorical_feature_names,
            return_cvbooster=True
        )

        cv_score = eval_results["valid ndcg@5-mean"][-1]

        print(f"CV-Score: {cv_score}")

        return 0.0
