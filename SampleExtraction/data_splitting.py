from typing import Tuple, List

import numpy as np
import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from ModelTuning import simulate_conf
from Persistence.RaceCardPersistence import RaceCardsPersistence
from SampleExtraction.RaceCardsSample import RaceCardsSample


class MonthDataSplitter:

    def __init__(
            self,
            container_upper_limit_percentage: float,
            n_months_test_sample: int,
            n_months_forward_offset: int,
            race_cards_folder: str
    ):
        self.container_upper_limit_percentage = container_upper_limit_percentage
        self.n_months_test_sample = n_months_test_sample
        self.n_months_forward_offset = n_months_forward_offset

        self.race_cards_loader = RaceCardsPersistence(race_cards_folder)
        file_names = self.race_cards_loader.race_card_file_names

        non_test_sample_file_names = file_names[self.n_months_forward_offset:-self.n_months_test_sample]
        self.container_file_names, self.train_file_names = np.split(
            non_test_sample_file_names,
            [
                int(len(non_test_sample_file_names) * self.container_upper_limit_percentage),
            ]
        )
        self.test_file_names = file_names[-self.n_months_test_sample:]

        if len(self.container_file_names) == 0:
            self.container_file_names = [self.train_file_names[0]]
            self.train_file_names = self.train_file_names[1:]

        self.n_non_test_months = len(self.container_file_names) + len(self.train_file_names)
