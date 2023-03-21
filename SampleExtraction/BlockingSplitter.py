from typing import Tuple, List

import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BlockingSplitter:

    def __init__(
            self,
            race_card_samples: RaceCardsSample,
            max_train_races: int,
            non_train_races_per_block: int,
            n_validation_blocks: int,
            n_test_blocks: int,
    ):
        self.max_train_races = max_train_races
        self.non_train_races_per_block = non_train_races_per_block
        self.n_validation_blocks = n_validation_blocks
        self.n_test_blocks = n_test_blocks

        race_cards_dataframe = race_card_samples.race_cards_dataframe
        self.race_ids = sorted(list(set(race_cards_dataframe[RaceCard.RACE_ID_KEY].values)))

        self.n_races = len(self.race_ids)

        print(self.n_races)

        n_races_min = (self.n_validation_blocks + self.n_test_blocks) * max_train_races + non_train_races_per_block
        if self.n_races < n_races_min:
            print(f"Train/Validation pool of size {self.n_races} too small. "
                  f"Needs at least size of {n_races_min}.")
            return -1

        race_number_df = pd.DataFrame(
            {
                RaceCard.RACE_ID_KEY: self.race_ids,
                "race_number": [i for i in range(len(self.race_ids))],
            }
        )

        self.race_cards_dataframe = race_cards_dataframe.merge(right=race_number_df, on=RaceCard.RACE_ID_KEY, how="inner").sort_values(by="race_number")

    def get_train_validation_split(self, nth_validation_block: int, n_train_races: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        return self.get_block_split(self.n_test_blocks + nth_validation_block, n_train_races)

    def get_train_test_split(self, nth_test_block: int, n_train_races: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        return self.get_block_split(nth_test_block, n_train_races)

    def get_block_split(self, nth_block: int, n_train_races: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_upper = self.n_races - self.non_train_races_per_block - nth_block * self.max_train_races
        train_lower = train_upper - n_train_races

        non_train_lower = train_upper
        non_train_upper = non_train_lower + self.non_train_races_per_block

        train_idx = [i for i in range(train_lower, train_upper)]
        validation_idx = [i for i in range(non_train_lower, non_train_upper)]

        return self.__split(train_idx, validation_idx)

    def __split(self, first_interval: List[int], second_interval: List[int]) -> Tuple[RaceCardsSample, RaceCardsSample]:
        first_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(first_interval)]
        second_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(second_interval)]

        return RaceCardsSample(first_df), RaceCardsSample(second_df)

    def get_last_n_races_sample(self, n: int) -> RaceCardsSample:
        last_n_races_interval = [self.n_races - 1 - i for i in range(n)]
        races_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(last_n_races_interval)]

        return RaceCardsSample(races_df)
