from typing import List

from Estimation.BoostedTreesRanker import BoostedTreesRanker
from SampleExtraction.FeatureManager import FeatureManager


class HyperParameterGrid:

    def __init__(self):
        self.__hyper_params = {}

    def add_parameter_values(self, parameter_name: str, parameter_values: List):
        self.__hyper_params[parameter_name] = parameter_values


class HyperParameterTuner:

    def __init(self, hyper_parameter_grid: HyperParameterGrid):
        self.__hyper_parameter_grid = HyperParameterGrid

    def run(self):
        for search_params in self.__hyper_parameter_grid:
            ranker = BoostedTreesRanker(FeatureManager.FEATURE_NAMES, search_params)

