import math
import os
from datetime import datetime
from typing import List

import pandas as pd
from SampleExtraction.RaceCardsSample import RaceCardsSample


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LeakageDetector:

    LIVE_SAMPLE_PATH: str = '../data/samples/latest_live_sample.csv'
    TEST_SAMPLE_PATH: str = '../data/samples/test_sample.csv'
    LEAKAGE_LOG_DIR_PATH: str = '../data/leakage_logs/'

    def __init__(self):
        self.columns_to_ignore = [
            "Unnamed: 0", "place_num", "place", "label",
            "current_win_odds", "current_place_odds", "regression_label", "has_won", "has_placed", "ranking_label"
        ]
        self.key_columns = ["race_name", "date_time", "name"]

    def save_live_data(self, live_sample: RaceCardsSample):
        live_sample.race_cards_dataframe.to_csv(self.LIVE_SAMPLE_PATH)

    def run(self) -> None:
        test_df = pd.read_csv(self.TEST_SAMPLE_PATH)
        live_df = pd.read_csv(self.LIVE_SAMPLE_PATH)

        mismatches = self.get_test_live_mismatches(test_df, live_df)

        print("\nLeakage detection run successfully with following result:")
        print("----------------------------------------------------------------------------------------------")

        if not mismatches:
            print(f"{BColors.OKGREEN}No leakage found")
        elif len(mismatches) <= 10:
            print(f"{BColors.FAIL}Some leakage found. Following mismatches between live and test data found: \n")
            for mismatch in mismatches:
                print(f"-> {mismatch}")
        else:
            leakage_path = os.path.join(self.LEAKAGE_LOG_DIR_PATH, datetime.today().strftime('%Y-%m-%d'))
            print(f"{BColors.FAIL}>10 mismatches between live and test data found. Log mismatches at: {leakage_path}")
            with open(leakage_path, 'w') as f:
                for mismatch in mismatches:
                    f.write(f"{mismatch}\n")

        print(f"{BColors.ENDC}----------------------------------------------------------------------------------------------\n")

    def get_test_live_mismatches(self, test_df: pd.DataFrame, live_df: pd.DataFrame) -> List[str]:
        mismatches = []

        merged_df = pd.merge(live_df, test_df, on=self.key_columns, how="inner")

        merged_df_columns = list(merged_df.columns)
        live_columns = list(live_df.columns)
        test_columns = list(test_df.columns)

        for column in merged_df_columns:
            mismatches += self.get_column_mismatches(column, live_columns, test_columns, merged_df)

        return mismatches

    def get_column_mismatches(self, column: str, live_columns: List[str], test_columns: List[str], merged_df: pd.DataFrame) -> List[str]:
        mismatches = []
        if column.endswith("_x"):
            base_column = column[:-2]
            if base_column not in self.columns_to_ignore:
                for index, row in merged_df.iterrows():
                    live_value = row[f"{base_column}_x"]
                    test_value = row[f"{base_column}_y"]
                    if live_value != test_value and (not math.isnan(live_value) or not math.isnan(test_value)):
                        row_key = f"{row['race_name']}/{row['date_time']}/{row['name']}. Live/Test Value: {live_value}/{test_value}"
                        mismatches.append(f"Feature: {base_column}, in row: {row_key}")
        elif not column.endswith("_y"):
            if f"{column}" not in live_columns:
                mismatches.append(f"Column {column} not found in live data.")
            if f"{column}" not in test_columns:
                mismatches.append(f"Column {column} not found in test data")

        return mismatches


def main():
    leakage_detector = LeakageDetector()
    leakage_detector.run()


if __name__ == '__main__':
    main()

    print("finished")

