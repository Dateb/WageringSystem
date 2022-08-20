from typing import Tuple

import pandas as pd
from pandas import DataFrame


class SampleSplitGenerator:

    def __init__(self, samples: DataFrame, train_width: int = 4, test_width: int = 3):
        samples["year-month"] = samples["date_time"].astype(str).str[:7]
        year_months_pairs = sorted(samples["year-month"].unique())
        year_months_pairs_df = pd.DataFrame(
            {
                "year-month": year_months_pairs,
                "fold_idx": [i for i in range(len(year_months_pairs))],
            }
        )

        self.train_width = train_width
        self.test_width = test_width

        self.validation_folds = [i for i in range(self.train_width, len(year_months_pairs) - test_width)]
        self.test_folds = [len(year_months_pairs) - i for i in range(1, test_width + 1)]

        self.samples = samples.merge(right=year_months_pairs_df, on="year-month", how="inner")

    def get_train_validation_split(self, nth_validation_fold: int) -> Tuple[DataFrame, DataFrame]:
        validation_fold_idx = self.validation_folds[nth_validation_fold]

        return self.__split(validation_fold_idx)

    def get_train_test_split(self, nth_test_fold: int):
        test_fold_idx = self.test_folds[nth_test_fold]

        return self.__split(test_fold_idx)

    def __split(self, last_fold_idx: int):
        train_folds = [last_fold_idx - i for i in range(1, self.train_width + 1)]

        train_samples = self.samples.loc[self.samples["fold_idx"].isin(train_folds)]
        last_fold_samples = self.samples.loc[self.samples["fold_idx"] == last_fold_idx]

        return train_samples, last_fold_samples
