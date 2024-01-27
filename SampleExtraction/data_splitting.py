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
            train_upper_limit_percentage: float,
            n_months_test_sample: int,
            n_months_forward_offset: int,
    ):
        self.container_upper_limit_percentage = container_upper_limit_percentage
        self.train_upper_limit_percentage = train_upper_limit_percentage
        self.n_months_test_sample = n_months_test_sample
        self.n_months_forward_offset = n_months_forward_offset

        self.race_cards_loader = RaceCardsPersistence(simulate_conf.RACE_CARDS_FOLDER_NAME)
        file_names = self.race_cards_loader.race_card_file_names

        non_test_sample_file_names = file_names[self.n_months_forward_offset:-self.n_months_test_sample]
        self.container_file_names, self.train_file_names, self.validation_file_names = np.split(
            non_test_sample_file_names,
            [
                int(len(non_test_sample_file_names) * self.container_upper_limit_percentage),
                int(len(non_test_sample_file_names) * self.train_upper_limit_percentage)
            ]
        )
        self.test_file_names = file_names[-self.n_months_test_sample:]

        if len(self.container_file_names) == 0:
            self.container_file_names = [self.train_file_names[0]]
            self.train_file_names = self.train_file_names[1:]

        self.n_non_test_months = len(self.container_file_names) + len(self.train_file_names) + len(self.validation_file_names)


class BlockSplitter:

    def __init__(
            self,
            race_card_sample: RaceCardsSample,
            n_test_races: int,
            n_validation_rounds: int = 5,
    ):
        # TODO: Handle case if n_test_races is too large!
        self.n_test_races = n_test_races
        self.block_count = n_validation_rounds

        race_cards_dataframe = race_card_sample.race_cards_dataframe

        self.race_ids = sorted(list(set(race_cards_dataframe[RaceCard.RACE_ID_KEY].values)))
        self.n_races = len(self.race_ids)
        self.train_validation_pool_size = self.n_races - n_test_races

        self.block_sizes = self.__get_block_sizes()
        self.block_intervals = []
        block_lower = 0
        for block_size in self.block_sizes:
            block_upper = block_lower + block_size
            block_interval = list(range(block_lower, block_upper))
            self.block_intervals.append(block_interval)
            block_lower = block_upper

        race_number_df = pd.DataFrame(
            {
                RaceCard.RACE_ID_KEY: self.race_ids,
                "race_number": [i for i in range(len(self.race_ids))],
            }
        )

        self.race_cards_dataframe = race_cards_dataframe.merge(right=race_number_df, on=RaceCard.RACE_ID_KEY, how="inner").sort_values(by="race_number")

        self.blocks = [self.__get_sample(block_interval) for block_interval in self.block_intervals]

        test_interval = [i for i in range(self.n_races - n_test_races, self.n_races)]
        self.test_sample = self.__get_sample(test_interval)

    def get_block_split(self, validation_block_idx: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        validation_sample = self.blocks[validation_block_idx]

        train_blocks = [
            self.blocks[j] for j in range(len(self.blocks)) if j != validation_block_idx
        ]

        train_dfs = [block.race_cards_dataframe for block in train_blocks]
        train_sample = RaceCardsSample(pd.concat(train_dfs))

        return train_sample, validation_sample

    def get_train_test_split(self) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i for i in range(self.n_races - self.n_test_races)]
        train_sample = self.__get_sample(train_interval)

        return train_sample, self.test_sample

    def __get_sample(self, block_interval: List[int]) -> RaceCardsSample:
        df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(block_interval)]

        return RaceCardsSample(df)

    def __get_block_sizes(self):
        block_size = self.train_validation_pool_size / self.block_count
        min_block_size = int(block_size)
        remainder_races = (block_size - min_block_size) * self.block_count
        additional_size = [1 if i < remainder_races else 0 for i in range(self.block_count)]

        return [min_block_size + additional_size[i] for i in range(self.block_count)]
