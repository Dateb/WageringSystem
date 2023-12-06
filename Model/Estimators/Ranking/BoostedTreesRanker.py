import lightgbm
import pandas as pd
from lightgbm import Dataset
from numpy import ndarray
from sklearn.preprocessing import LabelEncoder

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.Estimator import Estimator
from Model.Estimators.util.metrics import get_accuracy
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample
from sklearn.metrics import accuracy_score


class BoostedTreesRanker(Estimator):
    RANKING_SEED = 30

    FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "xendcg",
        "metric": "xendcg",
        # "verbose": -1,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
        "device": "cpu",

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
        self.booster = None

        self.categorical_feature_names = [feature.get_name() for feature in feature_manager.features if feature.is_categorical]
        self.cat_gbt_feature_names = [f"{cat_feature_name}_gbt" for cat_feature_name in self.categorical_feature_names]
        self.feature_names = self.feature_manager.numerical_feature_names + self.cat_gbt_feature_names

        # self.parameter_set = {**self.FIXED_PARAMS}

    def predict(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:

        for cat_feature_name in self.categorical_feature_names:
            cat_gbt_feature_name = f"{cat_feature_name}_gbt"
            train_sample.race_cards_dataframe[cat_gbt_feature_name] = train_sample.race_cards_dataframe[cat_feature_name].astype('category')
            validation_sample.race_cards_dataframe[cat_gbt_feature_name] = validation_sample.race_cards_dataframe[cat_feature_name].astype('category')
            test_sample.race_cards_dataframe[cat_gbt_feature_name] = test_sample.race_cards_dataframe[cat_feature_name].astype('category')

        self.fit_validate(train_sample, validation_sample)

        print("Model tuning completed!")
        self.score_test_sample(test_sample)

        train_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)
        validation_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)
        test_sample.race_cards_dataframe.drop(self.cat_gbt_feature_names, inplace=True, axis=1)

        print(f"Test accuracy gbt-model: {get_accuracy(test_sample)}")

        return test_sample.race_cards_dataframe["score"]

    def score_test_sample(self, test_sample: RaceCardsSample):
        race_cards_dataframe = test_sample.race_cards_dataframe
        X = race_cards_dataframe[self.feature_names]
        scores = self.booster.predict(X)

        test_sample.race_cards_dataframe["score"] = scores

    def fit_validate(self, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        self.booster = lightgbm.train(
            self.FIXED_PARAMS,
            train_set=self.get_dataset(train_sample.race_cards_dataframe),
            categorical_feature=self.cat_gbt_feature_names,
        )

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
