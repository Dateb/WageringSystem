import lightgbm
from numpy import ndarray
from DataAbstraction.Present.Horse import Horse
from Model.Estimators.Estimator import Estimator
from ModelTuning.ModelEvaluator import ModelEvaluator
from ModelTuning.RankerConfigMCTS.BetModelConfigurationTuner import BetModelConfigurationTuner
from SampleExtraction.BlockSplitter import BlockSplitter
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BoostedTreesRanker(Estimator):

    def __init__(self, feature_manager: FeatureManager, model_evaluator: ModelEvaluator, block_splitter: BlockSplitter):
        #TODO: Dont use block splitter as a property: instead hide the validation splitting inside the tuning routine
        super().__init__()
        self.feature_manager = feature_manager
        self.model_evaluator = model_evaluator
        self.block_splitter = block_splitter
        self.booster = None

    def predict(self, train_sample: RaceCardsSample, test_sample: RaceCardsSample) -> ndarray:
        self.tune_setting(train_sample)
        self.fit(train_sample)

        scores = self.booster.predict(test_sample.race_cards_dataframe[self.feature_names])

        return scores

    def tune_setting(self, train_sample: RaceCardsSample) -> None:
        configuration_tuner = BetModelConfigurationTuner(
            train_sample=train_sample,
            feature_manager=self.feature_manager,
            sample_splitter=self.block_splitter,
            model_evaluator=self.model_evaluator,
        )

        #TODO: Max iterations are fixed here
        self.best_configuration = configuration_tuner.search_for_best_configuration(max_iter_without_improvement=2)

        self.features = self.best_configuration.feature_subset
        self.feature_names = [feature.get_name() for feature in self.features]
        self.categorical_feature_names = [feature.get_name() for feature in self.features if feature.is_categorical]

        self.num_boost_rounds = self.best_configuration.num_boost_rounds

    def fit(self, train_sample: RaceCardsSample) -> None:
        self.booster = lightgbm.train(
            self.best_configuration.parameter_set,
            train_set=self.best_configuration.get_dataset(train_sample.race_cards_dataframe),
            categorical_feature=self.categorical_feature_names,
            num_boost_round=self.num_boost_rounds,
        )

        # importance_scores = self.booster.feature_importance(importance_type="gain")
        # feature_importances = {self.feature_names[i]: importance_scores[i] for i in range(len(importance_scores))}
        # sorted_feature_importances = {k: v for k, v in sorted(feature_importances.items(), key=lambda item: item[1])}
        # importance_sum = sum([importance for importance in list(feature_importances.values())])
        # print(f"{importance_sum}: {sorted_feature_importances}")
