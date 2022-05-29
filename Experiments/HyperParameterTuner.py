import itertools
from typing import List

import numpy as np
from tqdm import tqdm

from Betting.WinBettor import WinBettor
from DataAbstraction.RaceCard import RaceCard
from Estimation.BoostedTreesRanker import BoostedTreesRanker
from Estimation.SampleSet import SampleSet
from Experiments.ValidationScorer import ValidationScorer
from ModelTuning.Validator import Validator
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.FeatureManager import FeatureManager
from SampleExtraction.SampleEncoder import SampleEncoder


class HyperParameterGrid:

    def __init__(self):
        self.__param_names = []
        self.__param_values = []
        self.__counter = 0

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        if self.__counter >= len(self.__param_values):
            raise StopIteration
        parameter_values = self.__param_values[self.__counter]
        params = {}
        for i, param_name in enumerate(self.__param_names):
            params[param_name] = parameter_values[i]

        self.__counter += 1
        return params

    def __len__(self):
        return len(self.__param_values)

    def add_parameter_values(self, parameter_name: str, parameter_values: List):
        self.__param_names.append(parameter_name)

        if not self.__param_values:
            self.__param_values = parameter_values
        else:
            self.__param_values = list(itertools.product(self.__param_values, parameter_values))
        self.__counter = 0


class HyperParameterTuner:

    def __init__(self, hyper_parameter_grid: HyperParameterGrid):
        self.__hyper_parameter_grid = hyper_parameter_grid
        self.__bettor = WinBettor(kelly_wealth=1000)

        self.__raw_races = RaceCardsPersistence("train_race_cards").load_raw()
        race_cards = [
            RaceCard(race_id, self.__raw_races[race_id], remove_non_starters=False) for race_id in self.__raw_races
        ]

        sample_encoder = SampleEncoder(FeatureManager())
        samples = sample_encoder.transform(race_cards)
        self.__sample_set = SampleSet(samples)

        self.__best_score = 0

    def run(self):
        with tqdm(total=len(self.__hyper_parameter_grid)) as progress_bar:
            for search_params in self.__hyper_parameter_grid:
                estimator = BoostedTreesRanker(FeatureManager.FEATURE_NAMES, search_params)
                estimator.fit(self.__sample_set.samples_train)

                validator = Validator(estimator, self.__bettor, self.__sample_set, self.__raw_races)
                validation_scorer = ValidationScorer(validator)

                score = validation_scorer.score()

                if score > self.__best_score:
                    print(f"Found new best hyper parameters {search_params} with score: {score}")
                    self.__best_score = score

                progress_bar.update(1)


def main():
    hyper_parameter_grid = HyperParameterGrid()
    hyper_parameter_grid.add_parameter_values("num_leaves", list(np.arange(90, 100, 10)))
    hyper_parameter_grid.add_parameter_values("min_child_samples", list(np.arange(240, 260, 20)))

    hyper_parameter_tuner = HyperParameterTuner(hyper_parameter_grid)
    hyper_parameter_tuner.run()


if __name__ == '__main__':
    main()
    print("finished")
