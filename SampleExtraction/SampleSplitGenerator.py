from typing import Tuple, List

import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleSplitGenerator:

    def __init__(self, race_card_samples: RaceCardsSample, n_train: int, n_validation: int, n_folds: int):
        self.n_train = n_train
        self.n_validation = n_validation
        self.n_folds = n_folds
        last_idx = n_train + (n_folds + 1) * n_validation - 1
        print(last_idx)

        race_cards_dataframe = race_card_samples.race_cards_dataframe
        self.race_ids = list(set(race_cards_dataframe[RaceCard.RACE_ID_KEY].values))

        if last_idx >= len(self.race_ids):
            print(f"Splits are requiring {last_idx + 1} races. Only got {len(self.race_ids)}")
            return -1

        race_number_df = pd.DataFrame(
            {
                RaceCard.RACE_ID_KEY: self.race_ids,
                "race_number": [i for i in range(len(self.race_ids))],
            }
        )

        self.race_cards_dataframe = race_cards_dataframe.merge(right=race_number_df, on=RaceCard.RACE_ID_KEY, how="inner").sort_values(by="race_number")
        print(self.race_cards_dataframe["race_number"])

    def get_train_validation_split(self, nth_validation_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i + (self.n_validation * nth_validation_fold) for i in range(self.n_train)]
        validation_interval = [i + train_interval[-1] + 1 for i in range(self.n_validation)]

        return self.__split(train_interval, validation_interval)

    def get_train_test_split(self) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i + (self.n_validation * self.n_folds) for i in range(self.n_train)]
        test_interval = [i + train_interval[-1] + 1 for i in range(self.n_validation)]

        return self.__split(train_interval, test_interval)

    def __split(self, first_interval: List[int], second_interval: List[int]) -> Tuple[RaceCardsSample, RaceCardsSample]:
        first_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(first_interval)]
        second_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(second_interval)]

        return RaceCardsSample(first_df), RaceCardsSample(second_df)
