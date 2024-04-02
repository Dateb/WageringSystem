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

        self.feature_names = gbt_config.feature_names
        self.params = {**self.FIXED_PARAMS, **gbt_config.search_params}

        self.categorical_feature_names = [feature_name for feature_name in gbt_config.feature_names
                                          if feature_name in self.categorical_feature_names]
        dataset = dataset_factory.create_dataset(self.feature_names, self.categorical_feature_names)

        self.booster = lightgbm.train(
            num_boost_round=gbt_config.num_boost_round,
            params=gbt_config.search_params,
            train_set=dataset,
            categorical_feature=self.categorical_feature_names,
        )

        self.booster.free_dataset()

        return 0.0
