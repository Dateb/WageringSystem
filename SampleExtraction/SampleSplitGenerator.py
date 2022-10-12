from typing import Tuple, List

import pandas as pd

from DataAbstraction.Present.RaceCard import RaceCard
from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleSplitGenerator:

    def __init__(self, race_card_samples: RaceCardsSample, n_train_races: int, n_races_per_fold: int, n_folds: int):
        self.n_train_races = n_train_races
        self.n_races_per_fold = n_races_per_fold
        self.n_folds = n_folds
        last_idx = n_train_races + 2 * n_folds * n_races_per_fold - 1

        race_cards_dataframe = race_card_samples.race_cards_dataframe
        self.race_ids = sorted(list(set(race_cards_dataframe[RaceCard.RACE_ID_KEY].values)))
        self.n_races = len(self.race_ids)

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

    def get_train_validation_split(self, nth_validation_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i + (self.n_races_per_fold * nth_validation_fold) for i in range(self.n_train_races)]
        validation_interval = [i + train_interval[-1] + 1 for i in range(self.n_races_per_fold)]

        return self.__split(train_interval, validation_interval)

    def get_train_test_split(self, nth_test_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        train_interval = [i + (self.n_races_per_fold * (self.n_folds + nth_test_fold)) for i in range(self.n_train_races)]
        test_interval = [i + train_interval[-1] + 1 for i in range(self.n_races_per_fold)]

        return self.__split(train_interval, test_interval)

    def __split(self, first_interval: List[int], second_interval: List[int]) -> Tuple[RaceCardsSample, RaceCardsSample]:
        first_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(first_interval)]
        second_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(second_interval)]

        return RaceCardsSample(first_df), RaceCardsSample(second_df)

    def get_last_n_races_sample(self, n: int) -> RaceCardsSample:
        last_n_races_interval = [self.n_races - 1 - i for i in range(n)]
        print(last_n_races_interval)
        print(len(last_n_races_interval))
        races_df = self.race_cards_dataframe.loc[self.race_cards_dataframe["race_number"].isin(last_n_races_interval)]

        return RaceCardsSample(races_df)
