from typing import Tuple

import pandas as pd

from SampleExtraction.RaceCardsSample import RaceCardsSample


class SampleSplitGenerator:

    def __init__(self, race_card_samples: RaceCardsSample, train_width: int = 16, test_width: int = 5):
        race_cards_dataframe = race_card_samples.race_cards_dataframe
        race_cards_dataframe["year-month"] = race_cards_dataframe["date_time"].astype(str).str[:7]
        self.year_months_pairs = sorted(race_cards_dataframe["year-month"].unique())
        year_months_pairs_df = pd.DataFrame(
            {
                "year-month": self.year_months_pairs,
                "fold_idx": [i for i in range(len(self.year_months_pairs))],
            }
        )

        self.train_width = train_width
        self.test_width = test_width

        self.validation_folds = [i for i in range(self.train_width, len(self.year_months_pairs) - test_width)]
        self.test_folds = [len(self.year_months_pairs) - i for i in range(1, test_width + 1)]

        self.race_cards_dataframe = race_cards_dataframe.merge(right=year_months_pairs_df, on="year-month", how="inner")

    def get_train_validation_split(self, nth_validation_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        validation_fold_idx = self.validation_folds[nth_validation_fold]

        return self.__split(validation_fold_idx)

    def get_train_test_split(self, nth_test_fold: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        test_fold_idx = self.test_folds[nth_test_fold]

        return self.__split(test_fold_idx)

    def __split(self, last_fold_idx: int) -> Tuple[RaceCardsSample, RaceCardsSample]:
        #train_folds = [last_fold_idx - i for i in range(1, self.train_width + 1)]
        train_folds = [i for i in range(last_fold_idx)]

        train_dataframe = self.race_cards_dataframe.loc[self.race_cards_dataframe["fold_idx"].isin(train_folds)]
        last_fold_dataframe = self.race_cards_dataframe.loc[self.race_cards_dataframe["fold_idx"] == last_fold_idx]

        return RaceCardsSample(train_dataframe), RaceCardsSample(last_fold_dataframe)

    def get_year_month(self, fold_idx: int):
        return self.year_months_pairs[self.validation_folds[fold_idx]]
