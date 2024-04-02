from typing import List

import pandas as pd
from lightgbm import Dataset

from DataAbstraction.Present.RaceCard import RaceCard


class DatasetFactory:

    def __init__(self, sample: pd.DataFrame, label_name: str):
        self.sample = sample
        self.label_name = label_name

    def create_dataset(self, feature_names: List[str], categorical_feature_names: List[str]) -> Dataset:
        input_data = self.sample[feature_names]
        label = self.sample[self.label_name].astype(dtype="int")
        group = self.sample.groupby(RaceCard.RACE_ID_KEY)[RaceCard.RACE_ID_KEY].count()

        return Dataset(
            data=input_data,
            label=label,
            group=group,
            categorical_feature=categorical_feature_names,
        )
