from typing import Tuple, List

import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleSplitGenerator:

    def __init__(self, race_card_samples: RaceCardsSample, n_races_per_fold: int, n_folds: int):
        self.n_races_per_fold = n_races_per_fold
        self.n_folds = n_folds

        race_cards_dataframe = race_card_samples.race_cards_dataframe
        self.race_ids = sorted(list(set(race_cards_dataframe[RaceCard.RACE_ID_KEY].values)))

        self.n_races = len(self.race_ids)
        self.n_validation_races = self.n_races_per_fold
        self.n_test_races = self.n_races_per_fold
        self.n_train_validation_races = self.n_races - self.n_test_races

        print(self.n_train_validation_races)

        if self.n_train_validation_races < self.n_races_per_fold * self.n_folds:
            print(f"Train/Validation pool of size {self.n_train_validation_races} too small. "
                  f"Needs at least size of {self.n_races_per_fold * self.n_folds}.")
            return -1

        race_number_df = pd.DataFrame(
            {
                RaceCard.RACE_ID_KEY: self.race_ids,
                "race_number": [i for i in range(len(self.race_ids))],
            }
        )

        self.race_cards_dataframe = race_cards_dataframe.merge(right=race_number_df, on=RaceCard.RACE_ID_KEY, how="inner").sort_values(by="race_number")

    def get_train_validation_split(self, nth_validation_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        left_train_end = self.n_train_validation_races - self.n_races_per_fold * (nth_validation_fold + 1)
        train_idx_left = [i for i in range(0, left_train_end)]

        right_train_begin = self.n_train_validation_races - self.n_races_per_fold * nth_validation_fold
        train_idx_right = [i for i in range(right_train_begin, self.n_train_validation_races)]

        train_idx = train_idx_left + train_idx_right

        validation_idx = [i for i in range(left_train_end, right_train_begin)]

        return self.__split(train_idx, validation_idx)

    def get_train_test_split(self, nth_test_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i for i in range(0, self.n_train_validation_races)]
        test_interval = [i for i in range(self.n_train_validation_races, self.n_races)]

        return self.__split(train_interval, test_interval)

    def __split(self, first_interval: List[int], second_interval: List[int]) -> Tuple[RaceCardsSample, RaceCardsSample]:
        first_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(first_interval)]
        second_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(second_interval)]

        return RaceCardsSample(first_df), RaceCardsSample(second_df)

    def get_last_n_races_sample(self, n: int) -> RaceCardsSample:
        last_n_races_interval = [self.n_races - 1 - i for i in range(n)]
        races_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(last_n_races_interval)]

        return RaceCardsSample(races_df)
