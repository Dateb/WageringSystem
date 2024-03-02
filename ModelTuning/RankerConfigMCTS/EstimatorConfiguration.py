import random
from copy import copy
from typing import List

import lightgbm
import pandas as pd
from lightgbm import Dataset

from DataAbstraction.Present.Horse import Horse
from DataAbstraction.Present.RaceCard import RaceCard
from Model.Estimators.Estimator import Estimator
from Model.Estimators.estimated_probabilities_creation import WinProbabilizer
from SampleExtraction.Extractors.FeatureExtractor import FeatureExtractor
from SampleExtraction.RaceCardsSample import RaceCardsSample


class EstimatorConfiguration:

    ranking_seed = 30

    _FIXED_PARAMS: dict = {
        "boosting_type": "gbdt",
        "objective": "xendcg",
        "metric": "xendcg",
        "verbose": -1,
        "deterministic": True,
        "force_row_wise": True,
        "n_jobs": -1,
        "device": "cpu",

        "seed": ranking_seed,
        "data_random_seed": ranking_seed,
        "feature_fraction_seed": ranking_seed,
        "objective_seed": ranking_seed,
        "bagging_seed": ranking_seed,
        "extra_seed": ranking_seed,
        "drop_seed": ranking_seed,
    }

    probabilizer_values = [WinProbabilizer()]
    train_size_fraction_values = [1.0]
    num_boost_round_values = [100, 200, 500]
    stakes_fraction_values = [1.0]
    expected_value_additional_threshold_values = [0.0]
    lower_win_prob_threshold_values = [0]
    upper_win_prob_threshold_values = [1]
    learning_rate_values = [0.15]
    num_leaves_values = [2, 10, 30]
    min_child_samples_values = [200]

    n_decision_list: List[int]

    def __init__(
            self,
            decisions: List[int],
            base_features: List[FeatureExtractor],
            search_features: List[FeatureExtractor],
    ):
        self.probabilizer = None
        self.train_size_fraction = 1.0
        self.num_boost_rounds = 0
        self.stakes_fraction = 1.0
        self.expected_value_additional_threshold = 0.0

        self.search_params = {}
        self.parameter_set = {}

        self.label_name = Horse.HAS_WON_LABEL_KEY

        self.selected_features: List[FeatureExtractor] = copy(base_features)
        self.search_features = search_features
        self.selected_search_features = []
        self.n_decision_list = \
            [
                len(EstimatorConfiguration.probabilizer_values),
            ] + [2 for _ in range(len(search_features))]
        self.decisions = decisions
        self.is_terminal = False
        if len(decisions) == len(self.n_decision_list):
            self.is_terminal = True
            self.__init_config()

    def __init_config(self):
        for i, decision_idx in enumerate(self.decisions):
            self.__add_ith_decision(i, decision_idx)

    def __add_ith_decision(self, i: int, decision_idx: int):
        #TODO: Replace the long case logic
        if i == 0:
            self.probabilizer = self.probabilizer_values[decision_idx]
        if i >= 1 and decision_idx == 1:
            selected_search_feature = self.search_features[i - 1]
            self.selected_search_features.append(selected_search_feature)
            self.selected_features.append(selected_search_feature)

    def validate_estimator(self, estimator: Estimator, train_sample: RaceCardsSample, validation_sample: RaceCardsSample) -> float:
        self.parameter_set = {**self._FIXED_PARAMS, **self.search_params}

        estimator.feature_manager.selected_features = self.selected_features

        return -estimator.fit(train_sample, validation_sample)

        # cv_result = lightgbm.cv(
        #     self.parameter_set,
        #     metrics="MAP",
        #     train_set=self.get_dataset(sample.race_cards_dataframe),
        #     categorical_feature=self.categorical_feature_names,
        #     shuffle=False,
        #     num_boost_round=self.num_boost_rounds,
        #     nfold=5,
        # )
        #
        # return cv_result["valid map@1-mean"][-1]

    # def get_dataset(self, sample: pd.DataFrame) -> Dataset:
    #     group = sample.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()
    #
    #     return Dataset(
    #         data=input_data,
    #         label=label,
    #         group=group,
    #         categorical_feature=self.categorical_feature_names,
    #     )

    def get_full_decision_list(self) -> List[int]:
        full_decision_list = copy(self.decisions)
        for i in range(len(self.decisions), len(self.n_decision_list)):
            n_decisions = self.n_decision_list[i]
            next_decision = random.randrange(n_decisions)
            full_decision_list.append(next_decision)
        return full_decision_list

    def __str__(self) -> str:
        config_str = f"{type(self.probabilizer).__name__}/"\
                     f"train_size_fraction: {self.train_size_fraction}/"\
                     f"stakes_fraction:{self.stakes_fraction}/"\
                     f"ev_thresh:{self.expected_value_additional_threshold}/" \
                     f"boost_rounds:{self.num_boost_rounds}/search_params:{self.search_params}\n"
        return config_str

    @property
    def identifier(self) -> str:
        return str(self.decisions)

    @property
    def n_decisions_next_action(self):
        next_action_idx = len(self.decisions)
        return self.n_decision_list[next_action_idx]

